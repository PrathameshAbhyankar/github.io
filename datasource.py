import requests
import json
#from datetime import datetime
import datetime
import time

i = 1  

while True:  

       
        now = datetime.datetime.now()
        timestamp_new = now.strftime("%Y-%m-%d %H:%M:%S")
        name = "Bobby" + str(i)
        i = i + 1    
        data = json.dumps({
	    'timestamp': timestamp_new,
	    'transaction_id': '8d1e1533-6071-4b10-9cda-b8429c1c7a67',
	    'name': name,
	    'email': 'bobby.drake@pressure.io',
	    'age': 42,
	    'passport_number': 3847665,
	    'flight_from': 'Barcelona',
	    'flight_to': 'London',
	    'extra_bags': 1,
	    'flight_class': 'economy',
	    'priority_boarding': False,
	    'meal_choice': 'vegetarian',
	    'seat_number': '15D',
	    'airline': 'Red Balloon'
	})

        r = requests.post('https://api.us-east.tinybird.co/v0/events', 
        params = {
	    'name': 'project_specific',
	    'token': 'p.eyJ1IjogImM1YmRhY2YxLTI5YzUtNDIwZS1hYzMxLTY2OWJmMjAzZjBlZCIsICJpZCI6ICIwMmFiZWM0ZC0xM2VkLTRhYzItYmE1OS1iYzQ3YTE4ZTRlZjMiLCAiaG9zdCI6ICJ1c19lYXN0In0.vuZo6A9d9-gzyqQ0ftGBeJjvyfkzwilUqsIU2T8zWYE',
	}, 
	data=data)

        print(r.status_code)
        print(r.text)
        time.sleep(1)        	
