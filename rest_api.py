import json


class RestAPI(object):
    def __init__(self, database=None):
        self.database = database
        pass

    def get(self, endpoint, body=None):
        body = json.loads(body) if body else {}

        if endpoint == "/users":
            users = []
            if body:
                if body.get("users"):
                    found_users = list(filter(lambda user: user["name"] in body["users"], self.database.get("users")))
                    if not found_users:
                        print(f'Not able to find specified users {body["users"]}')
                        return {}
                    users += found_users
            else:
                for user in self.database.get("users"):
                    users.append(user)

            # Need to implement sorting of users by name TODO

            return bytes(json.dumps({"users": users}), "utf-8")

    def post(self, endpoint, body=None):
        body = json.loads(body) if body else {}
        if body:
            if endpoint == "/add" and body.get("user"):
                # search for the same user in the DB to make sure its not a duplicate
                same_name = list(filter(lambda user: user["name"] == body["user"], self.database.get("users")))
                # if all is good
                if not same_name:
                    new_user = {
                                "name": body["user"],
                                "owes": {},
                                "owed_by": {},
                                "balance": 0
                            }
                    try:
                        self.database.get("users").append(new_user)
                    except Exception as e:
                        print(e)
                    return bytes(json.dumps(new_user), "utf-8")
                else:
                    print(f'User with name {body["user"]} already exists in the database. Use another name')
                return bytes(json.dumps({}), "utf-8")

            elif endpoint == "/iou":
                if body.get("lender") and body.get("borrower") and body.get("amount"):
                    amount = body.get("amount")

                    # Validate lender and borrower exist in the database
                    lender_list = list(filter(lambda user: user["name"] == body["lender"], self.database.get("users")))
                    borrower_list = list(filter(lambda user: user["name"] == body["borrower"], self.database.get("users")))

                    if len(lender_list) != 1 or len(borrower_list) != 1:
                        print(f"Specified users are incorrect. Lender: {lender_list}. Borrower: {borrower_list}")
                        return bytes(json.dumps({}), "utf-8")

                    lender = lender_list[0]
                    borrower = borrower_list[0]

                    # Retrieve data for calculations
                    lender_name = lender["name"]
                    borrower_name = borrower["name"]
                    lender_owed_by = lender.get("owed_by").get(borrower_name) or 0
                    lender_owes = lender.get("owes").get(borrower_name) or 0
                    lender_balance = lender.get("balance")
                    borrower_owed_by = borrower.get("owed_by").get(lender_name) or 0
                    borrower_owes = borrower.get("owes").get(lender_name) or 0
                    borrower_balance = borrower.get("balance")

                    # Update database for lender and borrower
                    for a_dict in self.database.get("users"):
                        if a_dict.get('name', 0) == lender_name:
                            # Possible case:
                            # If lender already owes the borrower, then I should deduct from that amount first
                            # If there is a leftover, it should be added to owed_by
                            if lender_owes:
                                leftover = lender_owes - amount
                                if leftover == 0:
                                    a_dict['owes'].pop(borrower_name)
                                elif leftover < 0:
                                    a_dict['owed_by'].update({borrower_name: abs(leftover)})
                                    a_dict['owes'].pop(borrower_name)
                                else:
                                    a_dict['owes'].update({borrower_name: leftover})
                            else:
                                a_dict['owed_by'].update({borrower_name: lender_owed_by + amount})
                            a_dict['balance'] = lender_balance + amount

                        elif a_dict.get("name", 0) == borrower_name:
                            if borrower_owed_by:
                                leftover = borrower_owed_by - amount
                                if leftover == 0:
                                    a_dict['owed_by'].pop(lender_name)
                                elif leftover < 0:
                                    a_dict['owes'].update({lender_name: abs(leftover)})
                                    a_dict['owed_by'].pop(lender_name)
                                else:
                                    a_dict['owed_by'].update({lender_name: leftover})
                            else:
                                a_dict['owes'].update({lender_name: borrower_owes + amount})
                            a_dict['balance'] = borrower_balance - amount

                    return self.get("/users", bytes(json.dumps({"users": [lender_name, borrower_name]}), "utf-8"))

                else:
                    print(f"Incorrect body for POST /iou request")

                return bytes(json.dumps({}), "utf-8")
        else:
            print(f"Mandatory body was not provided for endpoint {endpoint}")

        pass