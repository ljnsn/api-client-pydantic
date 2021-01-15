from typing import List, Optional

from apiclient import APIClient, endpoint, paginated, retry_request
from pydantic import BaseModel, Field

from api_client_pydantic import serialize_all_methods


def by_query_params_callable(response, prev_params):
    if 'nextPage' in response and response['nextPage']:
        return {'page': response['nextPage']}


@endpoint(base_url='http://testserver')
class Urls:
    users = 'users'
    user = 'users/{id}'
    accounts = 'accounts'


class Client(APIClient):
    def get_request_timeout(self):
        return 0.1

    def list_users(self):
        return self.get(Urls.users)

    @retry_request
    def get_user(self, user_id: int):
        url = Urls.user.format(id=user_id)
        return self.get(url)

    def create_user(self, first_name, last_name):
        data = {'firstName': first_name, 'lastName': last_name}
        return self.post(Urls.users, data=data)

    def overwrite_user(self, user_id, first_name, last_name):
        data = {'firstName': first_name, 'lastName': last_name}
        url = Urls.user.format(id=user_id)
        return self.put(url, data=data)

    def update_user(self, user_id, first_name=None, last_name=None):
        data = {}
        if first_name:
            data['firstName'] = first_name
        if last_name:
            data['lastName'] = last_name
        url = Urls.user.format(id=user_id)
        return self.patch(url, data=data)

    def delete_user(self, user_id):
        url = Urls.user.format(id=user_id)
        return self.delete(url)

    @paginated(by_query_params=by_query_params_callable)
    def list_user_accounts_paginated(self, user_id):
        return self.get(Urls.accounts, params={'userId': user_id})


class UserID(BaseModel):
    user_id: int = Field(alias='userId')

    class Config:
        allow_population_by_field_name = True


class UserInfo(BaseModel):
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')

    class Config:
        allow_population_by_field_name = True


class User(UserID, UserInfo):
    class Config:
        allow_population_by_field_name = True


class UpdateUser(UserID):
    first_name: Optional[str] = Field(alias='firstName')
    last_name: Optional[str] = Field(alias='lastName')

    class Config:
        allow_population_by_field_name = True


class Account(BaseModel):
    account_name: str = Field(alias='accountName')
    number: str = Field(alias='number')

    class Config:
        allow_population_by_field_name = True


class AccountPage(BaseModel):
    results: List[Account]
    page: int
    next_page: Optional[int] = Field(alias='nextPage')

    class Config:
        allow_population_by_field_name = True


@serialize_all_methods()
class ClientWithPydantic(Client):
    def list_users(self) -> List[User]:
        return super().list_users()

    @retry_request
    def get_user(self, data: UserID) -> User:
        url = Urls.user.format(id=data['userId'])
        return self.get(url)

    def create_user(self, data: UserInfo) -> User:
        return self.post(Urls.users, data=data)

    def overwrite_user(self, data: User) -> User:
        url = Urls.user.format(id=data['userId'])
        return self.put(url, data=data)

    def update_user(self, data: UpdateUser) -> User:
        return self.patch(Urls.user.format(id=data['userId']), data=data)

    def delete_user(self, user_id: int) -> dict:
        return super().delete_user(user_id)

    @paginated(by_query_params=by_query_params_callable)
    def list_user_accounts_paginated(self, data: UserID) -> List[AccountPage]:
        return self.get(Urls.accounts, params=data)
