if __name__ == "__main__":
    import sys
    from streamlit.web import cli as stcli

    # Override sys.argv to call Streamlit from this script
    sys.argv = ["streamlit", "run", "src/app.py"]
    sys.exit(stcli.main())