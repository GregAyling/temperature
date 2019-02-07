import requests
from datetime import datetime
from calendar import monthrange
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

def _timeno(timetext):
	fulldays = timetext.split("/")[0]
	fullhours = timetext.split("/")[1].split(":")[0]
	if fullhours == "12":
		fullhours = "0"
	fullminutes = timetext.split(":")[1][:2]
	ampm = timetext[-2:]
	if ampm == "am":
		return float(fulldays) + float(fullhours)/24.0 + float(fullminutes)/(24.0*60) - 1
	else:
		return float(fulldays) + float(fullhours)/24.0 + float(fullminutes)/(24.0*60) - 0.5

if __name__ == "__main__":

	# Determine current day in month.
	now = datetime.now()

	# Split into components.
	current_day = now.day
	current_month = now.month
	current_year = now.year

	# Determine days in previous month.
	if current_month == 1:
		previous_month = 12
		previous_year = current_year - 1
	else:
		previous_month = now.month - 1
		previous_year = current_year
	previous_month_days = monthrange(previous_year, previous_month)[1]

	# Scrape data.
	page = requests.get("http://www.bom.gov.au/products/IDQ60901/IDQ60901.94576.shtml")
	soup = BeautifulSoup(page.content, 'html.parser')
	datetimes = soup.find_all(class_="rowleftcolumn")
	times = []
	temps = []
	apptemps = []
	for datetime_no in range(len(datetimes)):
		datetimedata = datetimes[datetime_no]
		readings=datetimedata.find_all("td")
		datetime_text = readings[0].get_text()
		tempreal = readings[1].get_text()
		tempapp = readings[2].get_text()
		# Only include data if real temperature data exists.
		if tempreal != "-":
			if _timeno(datetime_text) < current_day:
				times.append(_timeno(datetime_text))
			else:
				times.append(_timeno(datetime_text) - previous_month_days)
			temps.append(float(tempreal))
			apptemps.append(float(tempapp))	
			
	# Plot.
	plt.figure(figsize=(12,6))
	plt.title('Brisbane Weather Observations (last 3 days)', fontsize=18)
	plt.xlabel('Days Since Start of Month')
	plt.ylabel('Temperature')
	plt.grid(True)
	plt.scatter(times, temps)
	plt.scatter(times, apptemps)
	plt.axhline(y=20, color='blue', linestyle='-', linewidth=4)
	plt.axhline(y=30, color='red', linestyle='-', linewidth=4)
	plt.legend(['20 Celsius', '30 Celsius', 'Real Temperature', 'Apparent Temperature'], loc='upper left', shadow=True, facecolor='lightblue')

	# Maximise display window.
	mng = plt.get_current_fig_manager()
	mng.window.state('zoomed')

	# Show plot.
	plt.show()

