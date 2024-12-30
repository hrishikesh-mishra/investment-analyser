from mftool import Mftool
import streamlit as st,  pandas as pd, numpy as np, plotly.express as px , plotly.graph_objects as go
from yahooquery import Ticker
import datetime

from investments import investmentconfig

INVESTMENTS_FILE_FOLDER = "./investments/{file}.csv"
INVESTMENTS = investmentconfig.INVESTMENTS


def print_scheme_details(scheme_detail):
	st.markdown("#### Scheme Information:")
	st.divider()
	data  = {
	"Fund House:": scheme_detail["fund_house"],
	"Type:*" : scheme_detail["scheme_type"],
	"Category:" : scheme_detail["scheme_category"],
	"Code:" : str(scheme_detail["scheme_code"]),
	"Name:" : scheme_detail["scheme_name"],
	"Scheme Start Date:" : scheme_detail["scheme_start_date"]["date"],
	"Scheme Start NAV:" : str(scheme_detail["scheme_start_date"]["nav"])
	}

	df = pd.DataFrame([data])
	st.dataframe(df.iloc[0], use_container_width=True)


def investment_purchase_history(investment):
	st.markdown("#### Investment Purchase History:")
	st.divider()

	mf_data = mf.get_scheme_historical_nav(investment["code"], as_Dataframe=True)
	mf_data = mf_data.reset_index()
	mf_data["date"] = pd.to_datetime(mf_data["date"], dayfirst=True).sort_values()


	file = INVESTMENTS_FILE_FOLDER.format(file=investment["code"])

	my_invest_data =  pd.read_csv(file,  index_col=False)
	my_invest_data.drop_duplicates(inplace=True)
	my_invest_data = my_invest_data.reset_index()
	my_invest_data["date"] = pd.to_datetime(my_invest_data["date"], dayfirst=True).sort_values()


	mf_data = mf_data[mf_data['date'] >= my_invest_data["date"].min()]

	fig= px.line(mf_data.set_index("date")["nav"])
	fig.update_traces(line_color='rgb(0,0,255)')

	fig.add_trace(go.Scatter(x=my_invest_data["date"], y=my_invest_data["nav"],
		mode='lines+markers',
		name='All Investments (SIP + Lumpsum)',
		marker=dict(color='rgb(255,0,0)', size=6)))

	my_lumpsum_invest_data = my_invest_data[my_invest_data["sip_type"] == "Lumpsum"]
	fig.add_trace(go.Scatter(x=my_lumpsum_invest_data["date"], y=my_lumpsum_invest_data["nav"],
		mode='markers',
		name='Lumpsum',
		marker=dict(color='LightSkyBlue', size=8, symbol="diamond")))

	st.plotly_chart(fig)


def scheme_performance(scheme):
	st.markdown("#### Scheme Performance:")
	st.divider()

	ticker = Ticker(scheme['ticker'])

	st.markdown("<h5 style='text-align: center; color: LightSkyBlue;'>Scheme Holding Sectors</h1>", unsafe_allow_html=True)
	sector_weightings = ticker.fund_sector_weightings
	st.plotly_chart(px.bar(sector_weightings.sort_values(scheme['ticker']), orientation='h'))

	with st.expander("Detail Breakup"):
		st.write(ticker.fund_top_holdings[["holdingName", "holdingPercent"]])


	st.markdown("<h5 style='text-align: center; color: LightSkyBlue;'>Returns by scheme</h1>", unsafe_allow_html=True)


	start_date = st.date_input('**Start date**', (datetime.date.today()  - datetime.timedelta(days=3*265)))
	end_date = st.date_input('**End date**', datetime.date.today() )

	if start_date < end_date:
	    st.success('Start date: `%s` End date:`%s`' % (start_date, end_date))
	else:
	    st.error('Error: End date must fall after start date.')
	    return

	start_date = pd.to_datetime(start_date, format='%d-%m-%Y')
	end_date = pd.to_datetime(end_date, format='%d-%m-%Y')

	df = mf.get_scheme_historical_nav(scheme["code"], as_Dataframe=True).reset_index()
	df['nav'] = df['nav'].astype(float)
	df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
	df = df.sort_values('date')
	df = df.query("date >= @start_date and date <=@end_date").reset_index(drop=True)


	df['daily_returns'] = df['nav'].pct_change()
	df['cumulative_returns'] = (df['daily_returns']+1).cumprod()


	# df.plot(x='date', y='cumulative_returns', color='orange')
	# plt.title('Cumulative Returns Plot')
	# plt.plot

	fig= px.line(df, title="Cumulative Returns", x='date', y='cumulative_returns')
	fig.update_traces(line_color='#FFA500', line_width=2)
	st.plotly_chart(fig)

	with st.expander("Detail Breakup"):
		st.write(df)


def my_investment_analysis():
	selected_scheme_name = st.selectbox("Select a scheme",  [inv['name'] for inv in INVESTMENTS])
	selected_investment = next((item for item in INVESTMENTS if item["name"] == selected_scheme_name), None)

	print_scheme_details(mf.get_scheme_details(selected_investment["code"]))
	investment_purchase_history(selected_investment)
	scheme_performance(selected_investment)




def compare_navs(scheme_names):
	selectedSchemes = st.multiselect("Select schems to compare", options=list(scheme_names.keys()))
	if selectedSchemes:
		comparisionDF = pd.DataFrame()
		for scheme in selectedSchemes:
			code = scheme_names[scheme]
			data = mf.get_scheme_historical_nav(code, as_Dataframe=True)
			data = data.reset_index().rename(columns={"index" : "date"})
			data["date"] = pd.to_datetime(data["date"], dayfirst=True).sort_values()
			data["nav"] = data["nav"].replace(0, None).interpolate()
			comparisionDF[scheme] = data.set_index("date")["nav"]
		
		fig= px.line(comparisionDF, title="Comparision NAVs")
		st.plotly_chart(fig)



mf = Mftool()
st.title('Mutual Fund Financial Dashboard')
all_scheme_names = {v: k for k, v in mf.get_scheme_codes().items()}

option = st.sidebar.selectbox(
	"Choose an Action",
	[ "My Investments", "Compare NAVs"]
)


if option == "My Investments":
	st.header("My Investments:")
	my_investment_analysis()

if option == "Compare NAVs":
		st.header("Compare NAVs")
		compare_navs(all_scheme_names)



	


			



