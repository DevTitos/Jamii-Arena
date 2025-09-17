from hiero_sdk_python import Client, Network, AccountId, PrivateKey

client = Client(
    network=Network("testnet")
)

client.set_operator(AccountId.from_string("OPERATOR_ID"), private_key=PrivateKey.from_string("OPERATOR_KEY"))

from hiero_did_sdk_python import HederaDid

did = HederaDid(client=client, private_key_der="private_key_der")

await did.register()

await did.add_service(
    id_=f"{did.identifier}#service-1", service_type="LinkedDomains", service_endpoint="https://example.com/vcs"
)