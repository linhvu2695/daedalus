import website

app = website.create_app()

if __name__ == "__main__":
    app.run(debug=True)