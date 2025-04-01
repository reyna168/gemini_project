from typing import List, Optional
import json
import base64
import requests


class ContactPerson:
    def __init__(
        self,
        name: str,
        email: str,
        landline_number: str,
        cellphone_number: str,
        address: str,
        #image_base64: Optional[str] = None,
    ):
        self.name = name
        self.email = email
        self.landline_number = landline_number
        self.cellphone_number = cellphone_number
        self.address = address
        #self.image_base64 =image_base64
    
    def set_image_from_blob(self, blob: bytes):
        """從 BLOB 設定圖片"""
        #self.image = base64.b64encode(blob).decode('utf-8')
        #self.image_base64 = base64.b64encode(blob).decode('utf-8')
        #測試用
        #self.image_base64 = base64.b64encode(blob).decode('utf-8')
        self.image_base64 ="b'\xEF\xBB\xBF'"
        #self.image = base64.b64encode(blob).decode('ascii')


    # def __repr__(self):
    #     return (
    #         f"ContactPerson(name={self.name}, email={self.email}, landline_number={self.landline_number}, "
    #         f"cellphone_number={self.cellphone_number}, address={self.address}, image_base64={self.image_base64})"
    #     )
    def __repr__(self):
        return (
            f"ContactPerson(name={self.name}, email={self.email}, landline_number={self.landline_number}, "
            f"cellphone_number={self.cellphone_number}, address={self.address}"
        )


    # def to_dict(self):
    #     return {
    #         "name": self.name,
    #         "email": self.email,
    #         "landlineNumber": self.landline_number,
    #         "cellphoneNumber": self.cellphone_number,
    #         "address": self.address,
    #         "imageBase64": self.image_base64,
    #     }
    def to_dict(self):
        return {

            "name": self.name,
            "email": self.email,
            "landlineNumber": self.landline_number,
            "cellphoneNumber": self.cellphone_number,
            "address": self.address,

        }

class Company:
    def __init__(
        self,
        name: str,
        tax: str,
        tax_id_number: str,
        trade_method: str,
        #contact_persons: Optional[List[ContactPerson]] = None,
    ):
        self.name = name
        self.tax = tax
        self.tax_id_number = tax_id_number
        self.trade_method = trade_method
        #self.contact_persons = contact_persons if contact_persons else []

    # def __repr__(self):
    #     return (
    #         f"Company(name={self.name}, tax={self.tax}, tax_id_number={self.tax_id_number}, "
    #         f"trade_method={self.trade_method}, contact_persons={self.contact_persons})"
    #     )

    def __repr__(self):
        return (
            f"Company(name={self.name}, tax={self.tax}, tax_id_number={self.tax_id_number}, "
            f"trade_method={self.trade_method})"
        )
        

    def to_dict(self):

        #print(self.contact_persons.to_dict())
        print("xxx")
        return {
                      
            "name": self.name,
            "tax": self.tax,
            "taxIdNumber": self.tax_id_number,
            "tradeMethod": self.trade_method,
            #"contactPersons":[self.contact_persons.to_dict()]
            #"contactPersons": self.contact_persons.to_dict()]
           
        }
    
    # def to_dict(self):
    #     return {
             
    #         "name": self.name,
    #         "tax": self.tax,
    #         "taxIdNumber": self.tax_id_number,
    #         "tradeMethod": self.trade_method,

    #     }
    
    #def to_dict(self):
    #     return {
       
    #         "name": self.name,
    #         "tax": self.tax,
    #         "taxIdNumber": self.tax_id_number,
    #         "tradeMethod": self.trade_method,
    #         "contactPersons": [person.to_dict() for person in self.contact_persons],
            
    #     }
    
    def send_to_server(self, url: str):
        """將資料以 RESTful POST 傳送到伺服器，並處理回應"""
        headers = {'Content-Type': 'application/json'}
        payload = self.to_dict()
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print("Request successful! Response code: 200")
                return response.json()  # 回傳伺服器的回應資料
            else:
                print(f"Request failed. Response code: {response.status_code}")
                return {"error": response.text, "status_code": response.status_code}
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to server: {e}")
            return {"error": str(e)}

    def __str__(self):
        """以 JSON 格式輸出"""
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

# # Example usage with the provided data
# contact_person_data = ContactPerson(
#     name="Test contact rersons 2",
#     email="Test contact rersons 2",
#     landline_number="Test contact rersons 2",
#     cellphone_number="Test contact rersons 2",
#     address="Test contact rersons 2",
#     #image_base64="Test contact rersons 2",
# )

# company_data = Company(
#     name="Company Name 2",
#     tax="Company Name 2",
#     tax_id_number="Company Name 2",
#     trade_method="Company Name 2",
#     #contact_persons=[contact_person_data],
# )

#print(company_data.to_dict())
