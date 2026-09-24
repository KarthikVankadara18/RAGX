from FunctionCalling.RecoveryManager import RecoveryManager

def main():

    recovery = RecoveryManager()

    failed_step = {
        "step": 2,
        "action": "MEMORY_UPDATE",
        "query": "RAGX-Enterprise v3",
    }

    error = "No memory ID found for update."

    print()
    print("=" * 70)
    print("RECOVERY TEST")
    print("=" * 70)

    can_recover = recovery.can_recover(
        failed_step,
        error
    )

    print("Can recover:", can_recover)

    recovery_step = recovery.create_recovery_step(
        failed_step
    )

    print()
    print("Recovery step:")
    print(recovery_step)


if __name__ == "__main__":
    main()