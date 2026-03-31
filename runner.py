import traceback

if __name__ == "__main__":
    try:
        import test_appointment_flow
        test_appointment_flow.main()
    except Exception as e:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        print("Error captured to error_log.txt")
