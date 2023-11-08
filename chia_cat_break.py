'''Script to breakdown a Chia CAT into smaller amounts using RPC calls'''

import json
import time
import requests
import urllib3

urllib3.disable_warnings()

headers = {"Content-Type": "application/json"}
URL = "https://localhost:9256/"
cert = ("ssl/full_node/private_full_node.crt",
        "ssl/full_node/private_full_node.key")

## Constants
WALLET_BALANCE = "get_wallet_balance"
CAT_SPEND = "cat_spend"


def submit(URL, data, headers, cert):
    """needs to be submitted with URL call"""
    response = json.loads(
        requests.post(URL, data=data, headers=headers, cert=cert,
                      verify=False).text)
    return json.dumps(response, indent=4, sort_keys=True)


def get_wallet_balance(wallet_id):
    """shows the balance of all synced wallets"""
    data = '{"wallet_id": "%s"}' % wallet_id
    result = submit(URL + WALLET_BALANCE, data, headers, cert)
    return json.loads(result)


def spend_cat(address, wallet_id, spend_amount, fee):
    """send CAT transaction"""
    data = '{"wallet_id": %s, "amount": %s, "fee": %s, "inner_address": "%s"}' % (
        int(wallet_id),
        int(spend_amount),
        int(fee),
        address.strip(),
    )
    result = submit(URL + CAT_SPEND, data, headers, cert)
    return json.loads(result)


def break_coin(address, wallet_id, spend_amount, fee, min_size):
    '''Breaks down coin into smaller amounts'''
    while spend_amount > min_size:
        if (get_wallet_balance(wallet_id)["wallet_balance"]
            ["spendable_balance"] >= spend_amount and
                get_wallet_balance(1)["wallet_balance"]["spendable_balance"] >
                0):
            spent = spend_cat(address, wallet_id, spend_amount, fee)
            print(f"\n{spent}")
            if bool(spent["success"]) and spend_amount > 0:
                print(spend_amount)
                spend_amount = int((((spend_amount / min_size) // 2) - 1) * min_size)

            else:

                time.sleep(20)
        else:
            print("\nNo spendable balance")
            time.sleep(30)
        
        


if __name__ == "__main__":
    try:
        address = input("Enter the XCH address to send the breakdown: ")
        min_size = int(
            input("Enter smallest size you wish to breakdown CAT: ")
        )  # For example use 1000 if you only want coins broken down into no smaller then 1 CAT
        wallet_id = int(
            (input("Enter wallet number of the CAT you wish to breakdown: ")
             ))  # Wallet Number is based on number of CATS down in wallet
        wallet = get_wallet_balance(wallet_id)
        print(f"\nReview and confirm this is the correct wallet: {wallet}")
        correct_wallet = input("Correct: Y/N? ").upper().strip()
        if correct_wallet == "Y":
            fee = int(
                input("\nEnter fee amount in Mojo for each breakdown: ").strip(
                ))  # in mojo
            spend_amount = int(
                (wallet["wallet_balance"]["spendable_balance"]) // 2)
            confirm = (input(
                f"\nWallet ID = {wallet_id} \nSpend amount = {spend_amount} \nFee = {fee}\nConfirm details are correct (Y/N?): "
            ).upper().strip())
            if confirm == "Y":
                break_coin(address, wallet_id, spend_amount, fee, min_size)
            else:
                print("CAT not sent")

    except ValueError:
        print("\nPlease enter Integer Value only when requested!")
