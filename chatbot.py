from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load and clean the data
file_path = "Data Analysis.csv"
df = pd.read_csv(file_path)

# Drop an unnecessary column if it exists
df = df.drop(columns=["Unnamed: 10"], errors="ignore")

# Reshape the data
df_long = df.melt(id_vars=["Metric"], var_name="Company_Year", value_name="Value")
df_long["Company"] = df_long["Company_Year"].str.extract(r"^(\w+)")
df_long["Year"] = df_long["Company_Year"].str.extract(r"(\d{4})").astype(int)
df_long["Value"] = df_long["Value"].replace({r"[\$,]": ""}, regex=True).astype(float)

# Pivot the data for analysis
df_clean = df_long.pivot_table(index=["Company", "Year"], columns="Metric", values="Value").reset_index()
df_clean.columns.name = None
df_clean = df_clean.rename(columns={"Total Revenue": "Total Revenue (USD)", "Net Income": "Net Income (USD)"})
df_clean["Revenue Growth (%)"] = df_clean.groupby("Company")["Total Revenue (USD)"].pct_change() * 100
df_clean["Net Income Growth (%)"] = df_clean.groupby("Company")["Net Income (USD)"].pct_change() * 100

# Aggregate data
company_aggregates = df_clean.groupby("Company")[["Total Revenue (USD)", "Net Income (USD)"]].sum()
avg_growth_by_company = df_clean.groupby("Company")[["Revenue Growth (%)", "Net Income Growth (%)"]].mean()
year_aggregates = df_clean.groupby("Year")[["Total Revenue (USD)", "Net Income (USD)"]].sum()

# Chatbot logic
def financial_chatbot(user_query):
    if "total revenue for Apple" in user_query:
        return f"The total revenue for Apple is {company_aggregates.loc['Apple', 'Total Revenue (USD)']:.2f} USD."
    elif "total revenue for Microsoft" in user_query:
        return f"The total revenue for Microsoft is {company_aggregates.loc['Microsoft', 'Total Revenue (USD)']:.2f} USD."
    elif "average revenue growth for Microsoft" in user_query:
        growth = avg_growth_by_company.loc['Microsoft', 'Revenue Growth (%)']
        return f"The average revenue growth for Microsoft is {growth:.2f}%."
    elif "aggregate total revenue by year" in user_query:
        totals = year_aggregates['Total Revenue (USD)'].to_dict()
        return "Aggregate total revenue by year:\n" + "\n".join([f"{year}: {revenue:.2f} USD" for year, revenue in totals.items()])
    else:
        return "Sorry, I can only provide information on predefined queries."

# Define Flask routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.form["query"]
    response = financial_chatbot(user_query)
    return render_template("index.html", user_query=user_query, response=response)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
