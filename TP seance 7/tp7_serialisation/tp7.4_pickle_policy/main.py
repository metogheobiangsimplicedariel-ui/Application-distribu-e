from hmac_signature import sign_payload, verify_payload


def run():
    print("=" * 60)
    print("TP7.4 - Politique de serialisation sure")
    print("=" * 60)

    print("(Voir le fichier safe_serialization_policy.md pour le tableau et la checklist complets)")

    print("\nEXEMPLE HMAC")
    print("-" * 40)
    data = {"id": 42, "title": "Document secret"}
    payload, sig = sign_payload(data)
    print(f"Payload: {payload}")
    print(f"Signature: {sig[:32]}...")
    print(f"Verification: {'OK' if verify_payload(payload, sig) else 'ECHEC'}")


if __name__ == "__main__":
    run()
