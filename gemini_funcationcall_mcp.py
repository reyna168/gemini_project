import argparse
import asyncio
import os
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client



def parse_args():
    parser = argparse.ArgumentParser(description="透過 Gemini 自動呼叫工具並產生結果")
    parser.add_argument(
        "--required_tools",
        type=str,
        default="count_r,count_l,count_e",
        help="必要使用的工具名稱，使用逗號分隔"
    )
    parser.add_argument(
        "--base_prompt",
        type=str,
        default="請使用工具計算下列三個字：「role」、「retroreflector」與「rewrite」中分別包含幾個字母 r, e。",
        help="原始提示語"
    )
    return parser.parse_args()

GOOGLE_API_KEY = ""


client = genai.Client(api_key = GOOGLE_API_KEY)

server_params = StdioServerParameters(
    command="python",
    args=["mcpserver_2.py"]
)


async def ask_gemini(prompt, tools=None, temperature=0):
    return client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(temperature=temperature, tools=tools),
    )


async def judge_if_answerable(base_prompt, tool_outputs):
    prompt = (
        f"原始問題：{base_prompt}\n\n"
        f"目前可用資訊：\n{chr(10).join(tool_outputs)}\n\n"
        "請你只回答 '可以回答' 或 '無法回答'，不要提供解釋。"
    )
    response = await ask_gemini(prompt)
    return response.candidates[0].content.parts[0].text.strip()


async def ask_missing_info(base_prompt, tool_outputs):
    prompt = (
        f"原始問題：{base_prompt}\n\n"
        f"目前可用資訊：\n{chr(10).join(tool_outputs)}\n\n"
        "你無法完整回答問題，請指出還需要哪些資訊（簡短列出）。"
    )
    response = await ask_gemini(prompt)
    return response.candidates[0].content.parts[0].text.strip()


async def run():
    
    args = parse_args()
    required_tools = set(t.strip() for t in args.required_tools.split(","))
    base_prompt = args.base_prompt

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await session.list_tools()

            tools = [
                {
                    "function_declarations": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                k: v for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        }
                    ]
                } for tool in mcp_tools.tools
            ]

            print(f"\n🚀 初始問題: {base_prompt}")
            initial_response = await ask_gemini(base_prompt, tools=tools)
            parts = initial_response.candidates[0].content.parts

            tool_outputs = []
            used_tools = set()

            for part in parts:
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    print(f"🛠 呼叫工具: {fc.name}, args: {fc.args}")
                    used_tools.add(fc.name)
                    result = await session.call_tool(fc.name, arguments=fc.args)
                    output_text = result.content[0].text
                    print(f"📦 工具結果: {output_text}")
                    tool_outputs.append(f"工具 `{fc.name}` 回傳：{output_text}")
                elif hasattr(part, "text"):
                    print("🧠 Gemini 輸出：", part.text)

            decision = await judge_if_answerable(base_prompt, tool_outputs)

            if "可以回答" in decision:
                print("\n✅ 已獲足夠資訊，準備產出最終回答")
                final_prompt = (
                    f"原始問題：{base_prompt}\n\n以下是你取得的資訊：\n{chr(10).join(tool_outputs)}\n\n請根據這些資訊，回答使用者的問題。"
                )
                final_response = await ask_gemini(final_prompt)
                print("==========")
                print("🧾 最終回答：", final_response.candidates[0].content.parts[0].text)
            else:
                print("\n⚠️ 資訊不足，無法完整回答。")
                missing_info = await ask_missing_info(base_prompt, tool_outputs)
                print("🔍 Gemini 判斷還需要：", missing_info)
                # 此處可以擴充實作: 根據 missing_info 再決定呼叫哪些 tool，進行下一輪嘗試


asyncio.run(run())