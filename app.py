from flask import Flask, render_template, request
import pymysql as sql
app = Flask(__name__)


mydb = sql.connect(
    host="db4free.net",
    port=3306,
    user="menyawinoo",
    password="Lol.01001647050",
    database="propertyfinderzz"
)

# Select Destinct Areas for areas of interest

mycursor = mydb.cursor()

sql_distinct_areas = """
select distinct prop_Area from property;
"""

sql_agent_numbers = """
select review_Agent_Number from review;
"""

sql_broker_names = """
select broker_Name from brokercompany;
"""

sql_property_cities = """
select distinct prop_City from property;
"""

sql_property_types = """
select distinct prop_type from property;
"""

sql_amenities = """
select distinct prop_Amenity from amenities;
"""

sql_brokers_agg = """
SELECT B.broker_Name FROM brokercompany B 
JOIN agent A on(B.broker_Name = A.Agent_Broker) 
JOIN review R on(R.review_Agent_Number = A.Agent_Number) 
GROUP by 1;
"""

sql_dev = """
select distinct project_Name from devproject
"""

mycursor.execute(sql_distinct_areas)
DistinctAreas = mycursor.fetchall()

print(DistinctAreas)
mycursor.execute(sql_agent_numbers)
AgentNumbers = mycursor.fetchall()


mycursor.execute(sql_broker_names)
BrokerNames = mycursor.fetchall()


mycursor.execute(sql_property_cities)
PropertyCities = mycursor.fetchall()


mycursor.execute(sql_property_types)
PropertyTypes = mycursor.fetchall()

mycursor.execute(sql_amenities)
Amenities = mycursor.fetchall()

mycursor.execute(sql_brokers_agg)
aggBrokers = mycursor.fetchall()

mycursor.execute(sql_dev)
Developers = mycursor.fetchall()

print("Tmam")


@app.route("/")
def select():
    return render_template("index.html")


# Register a user

@app.route("/enteruser", methods=['POST', 'GET'])
def enteruser():
    return render_template("enter_user.html", list=DistinctAreas)


@app.route("/user_enter", methods=['POST', 'GET'])
def user_enter():
    if request.method == 'POST':
        gender = request.form["Gender"]
        username = request.form["user_Name"]
        userFName = request.form["user_FName"]
        userLName = request.form["user_LName"]
        userBdate = request.form["user_BDate"]
        userAofFocus = request.form["user_AofFocus"]
        userEmail = request.form["user_Email"]
        userPhone = request.form["user_Phone"]

        sql1 = """
            INSERT INTO users
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        val = (gender, username, userFName, userLName,
               userBdate, userAofFocus, userEmail, userPhone)
        mycursor.execute(sql1, val)

        mydb.commit()

    return render_template("index.html", list=DistinctAreas)


# Add a new user review on an agent

@app.route("/enterreview", methods=['POST', 'GET'])
def enterreview():
    return render_template("enter_review.html")


@app.route("/review_enter", methods=['POST', 'GET'])
def review_enter():
    if request.method == 'POST':
        reviewRating = request.form["Review_Rating"]
        reviewTextual = request.form["Review_Textual"]
        reviewUserEmail = request.form["Review_User_Email"]
        reviewAgentNumber = request.form["Review_Agent_Number"]
        reviewAgentID = request.form["ID"]

        sql2 = """
            INSERT INTO review
            VALUES (%s, %s, %s, %s, %s)
            """

        val2 = (reviewRating, reviewTextual, reviewUserEmail,
                reviewAgentNumber, reviewAgentID)
        mycursor.execute(sql2, val2)

        mydb.commit()
    return render_template("index.html")


# View existing reviews of a given agent

@app.route("/viewreview", methods=['POST', 'GET'])
def viewreview():
    return render_template("view_reviews_number.html", list=AgentNumbers)


@app.route("/review_view", methods=['POST', 'GET'])
def review_view():
    if request.method == 'POST':
        requestedAgent = request.form["agent_Phone"]
        requestedAgent = requestedAgent.replace('(\'', '').replace('\')', '')
        requestedAgent = requestedAgent.replace("',)", '').replace('\')', '')
        print(requestedAgent)
        sql3 = """
            SELECT * FROM review
            WHERE review_Agent_Number = "{}";
            """.format(requestedAgent)
        print(sql3)
        mycursor.execute(sql3)
        reviews = mycursor.fetchall()
        print(reviews)

    headings = ("Rating", "Text", "User Email",
                "Agent Number", "Review ID")
    return render_template('reviews.html', reviews=reviews, headings=headings)


# View aggregated rating of a brokerage company

@app.route("/viewagg", methods=['POST', 'GET'])
def viewagg():
    return render_template("select_broker_agg.html", list=aggBrokers)


@app.route("/agg_view", methods=['POST', 'GET'])
def agg_view():
    if request.method == 'POST':
        requestedBrokeragg = request.form["broker_Name"]
        requestedBrokeragg = requestedBrokeragg.replace(
            '(\'', '').replace('\')', '')
        requestedBrokeragg = requestedBrokeragg.replace(
            "',)", '').replace('\')', '')

        sql4 = """
            SELECT B.broker_Name, avg(R.review_Rating) FROM brokercompany B 
            JOIN agent A on(B.broker_Name = A.Agent_Broker) 
            JOIN review R on(R.review_Agent_Number = A.Agent_Number) 
            WHERE B.broker_Name = "{}" GROUP by 1;
            """.format(requestedBrokeragg)

        mycursor.execute(sql4)

        rating = mycursor.fetchall()
        print(rating)
    headings = ("Broker Company Name", "Aggregated Rating")
    return render_template('reviews.html', reviews=rating, headings=headings)


# Show the location of a given development,
# along with the average price / sqm and the number of listings for each unit type

@app.route("/viewdev", methods=['POST', 'GET'])
def viewdev():
    return render_template("select_dev.html", list=Developers)


@app.route("/dev_view", methods=['POST', 'GET'])
def dev_view():
    if request.method == 'POST':
        devName = request.form["dev_Name"]
        devName = devName.replace(
            '(\'', '').replace('\')', '')
        devName = devName.replace(
            "',)", '').replace('\')', '')

        sql4 = """
            SELECT project_Location, project_PPerSqft, project_Units 
            FROM devproject 
            WHERE project_Name = "{}"
            """.format(devName)
        print(sql4)
        mycursor.execute(sql4)

        rating = mycursor.fetchall()
    headings = ("Development Project Name",
                "Price per Sqft", "Number of Units")
    return render_template('reviews.html', reviews=rating, headings=headings)

# Show all the properties in a certain city in a given price range,
# with a given set of amenities


@app.route("/viewprop", methods=['POST', 'GET'])
def viewprop():
    return render_template("view_property.html", list=PropertyCities, list2=PropertyTypes)


@app.route("/prop_view", methods=['POST', 'GET'])
def prop_view():
    if request.method == 'POST':
        propertyCity = request.form["prop_City"]
        propertyCity = propertyCity.replace('(\'', '').replace('\')', '')
        propertyCity = propertyCity.replace("',)", '').replace('\')', '')
        print(propertyCity)

        propertyType = request.form["prop_Type"]
        propertyType = propertyType.replace('(\'', '').replace('\')', '')
        propertyType = propertyType.replace("',)", '').replace('\')', '')
        print(propertyType)

        sql5 = """
            SELECT prop_Title, prop_priceEGP FROM property
            WHERE prop_City = "{}" and prop_type = "{}"
            """.format(propertyCity, propertyType)
        print(sql5)

        mycursor.execute(sql5)

        rating = mycursor.fetchall()
        print(rating)
    headings = ("Property Title", "Property Price")
    return render_template('reviews.html', reviews=rating, headings=headings)


# Show all the properties in a certain city in a given price range, with a given
# set of amenities

@app.route("/viewpropam", methods=['POST', 'GET'])
def viewpropam():
    return render_template("filter_prop_amenities.html", list=PropertyCities, amenities=Amenities)


@app.route("/prop_view_amenity", methods=['POST', 'GET'])
def prop_view_amenity():
    if request.method == 'POST':
        propertyCity = request.form["prop_City"]
        propertyCity = propertyCity.replace('(\'', '').replace('\')', '')
        propertyCity = propertyCity.replace("',)", '').replace('\')', '')

        try:
            Unfurnished = request.form["Unfurnished"]
        except:
            Unfurnished = ""

        try:
            built = request.form["Built in Wardrobes"]
        except:
            built = ""
        try:
            concierge = request.form["Concierge"]
        except:
            concierge = ""
        try:
            pets = request.form["Pets Allowed"]
        except:
            pets = ""
        try:
            security = request.form["Security"]
        except:
            security = ""
        try:
            spa = request.form["Shared Spa"]
        except:
            spa = ""
        try:
            landmark = request.form["View of Landmark"]
        except:
            landmark = ""
        try:
            barbecue = request.form["Barbecue Area"]
        except:
            barbecue = ""
        try:
            play = request.form["Children's Play Area"]
        except:
            play = ""
        try:
            pool = request.form["Children's Pool"]
        except:
            pool = ""
        try:
            parking = request.form["Covered Parking"]
        except:
            parking = ""
        try:
            lobby = request.form["Lobby in Building"]
        except:
            lobby = ""
        try:
            gym = request.form["Shared Gym"]
        except:
            gym = ""
        try:
            spool = request.form["Shared Pool"]
        except:
            spool = ""
        try:
            water = request.form["View of Water"]
        except:
            water = ""
        try:
            ac = request.form["Central A/C"]
        except:
            ac = ""
        try:
            kitchen = request.form["Kitchen Appliances"]
        except:
            kitchen = ""
        try:
            maid = request.form["Maid Service"]
        except:
            maid = ""
        try:
            maidr = request.form["Maids Room"]
        except:
            maidr = ""
        try:
            pgarden = request.form["Private Garden"]
        except:
            pgarden = ""
        try:
            pgym = request.form["Private Gym"]
        except:
            pgym = ""
        try:
            pjac = request.form["Private Jacuzzi"]
        except:
            pjac = ""
        try:
            ppool = request.form["Private Pool"]
        except:
            ppool = ""
        try:
            study = request.form["Study"]
        except:
            study = ""
        try:
            closet = request.form["Walk-in Closet"]
        except:
            closet = ""
        try:
            furnished = request.form["Furnished"]
        except:
            furnished = ""
        try:
            pfurnished = request.form["Partly furnished"]
        except:
            pfurnished = ""

        sql6 = """
            SELECT DISTINCT prop_Title, prop_priceEGP FROM property P 
            Join amenities A on(A.prop_Amenities_ID = P.prop_ID)
            WHERE P.prop_City = "{}" 
            """.format(propertyCity)

        if Unfurnished == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Unfurnished'"

        if built == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Built in Wardrobes'"

        if concierge == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Concierge'"

        if pets == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Pets Allowed'"

        if security == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Security'"

        if spa == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Shared Spa'"

        if landmark == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'View of Landmark'"

        if barbecue == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Barbecue Area'"

        if play == "on":
            sql6 = sql6 + \
                " AND A.prop_Amenity = {}".format("Children's Play Area")

        if pool == "on":
            sql6 = sql6 + " AND A.prop_Amenity = {}".format("Children's Pool")

        if parking == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Covered Parking'"

        if lobby == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Lobby in Building'"

        if gym == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Shared Gym'"

        if spool == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Shared Pool'"

        if water == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'View of Water'"

        if ac == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Central A/C'"

        if kitchen == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Kithcen Appliances'"

        if maid == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Maid Service'"

        if maidr == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Maids Room'"

        if pgarden == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Private Garden'"

        if pgym == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Private Gym'"

        if pjac == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Private Jacuzzi'"

        if ppool == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Private Pool'"

        if study == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Study'"

        if closet == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Walk-in Closet'"

        if furnished == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Furnished'"

        if pfurnished == "on":
            sql6 = sql6 + " AND A.prop_Amenity = 'Partly furnished'"

        print(sql6)
        mycursor.execute(sql6)

        properties = mycursor.fetchall()
        print(properties)
        headings = ("Property Title", "Property Price")
    return render_template('reviews.html', reviews=properties, headings=headings)


# Show the top 10 areas in a given city by amount of inventory and price / sqm
# of a given unit type

@app.route("/viewtop10", methods=['POST', 'GET'])
def viewtop10():
    return render_template("select_top_areas.html", list=PropertyCities, list2=PropertyTypes)


@app.route("/top10_view", methods=['POST', 'GET'])
def top_areas_view():
    if request.method == 'POST':
        propertyCity = request.form["prop_City"]
        propertyCity = propertyCity.replace('(\'', '').replace('\')', '')
        propertyCity = propertyCity.replace("',)", '').replace('\')', '')

        propertyType = request.form["prop_Type"]
        propertyType = propertyType.replace('(\'', '').replace('\')', '')
        propertyType = propertyType.replace("',)", '').replace('\')', '')

        sql7 = """
            SELECT distinct prop_Area,  prop_City FROM property
            WHERE prop_City = "{}" and prop_Type = "{}"
            """.format(propertyCity, propertyType)

        print(sql7)

        mycursor.execute(sql7)
        areas = mycursor.fetchall()
        print(areas)
        headings = ("Area", "City")
    return render_template('reviews.html', reviews=areas, headings=headings)

# Show the top 5 brokerage companies by the amount of listings they have,
# along with their avg price / sqm, number of agents, and average listings per agent


@app.route("/top5_view", methods=['POST', 'GET'])
def top5_view():

    sql7 = """
    SELECT B.broker_Name, B.broker_Active_Listings, 
    AVG(prop_priceEGP/prop_size_sqm), COUNT(*), Count(*)
    from brokercompany B 
    JOIN property P on(B.broker_Number = P.prop_Broker_Number) 
    JOIN agent A on(A.Agent_Broker = B.broker_Name) 
    GROUP BY B.broker_Name ORDER BY 2 DESC LIMIT 5;
    """

    print(sql7)

    mycursor.execute(sql7)
    areas = mycursor.fetchall()
    print(areas)
    headings = ("Broker Company Name", "Active Listings", "Average Price",
                "Number of Agents", "Number of listings per Agent")
    return render_template('reviews.html', reviews=areas, headings=headings)


# Show all the properties listed by a specific agent
# (given their first and last name and / or phone no)


@app.route("/viewagent", methods=['POST', 'GET'])
def viewagent():
    return render_template("select_agent.html", list=AgentNumbers)


@app.route("/agent_view", methods=['POST', 'GET'])
def agent_view():
    if request.method == 'POST':
        agentNumber = request.form["agent_Phone"]
        agentNumber = agentNumber.replace('(\'', '').replace('\')', '')
        agentNumber = agentNumber.replace("',)", '').replace('\')', '')
        sql7 = """
            SELECT P.prop_Title, P.prop_priceEGP FROM property P 
            JOIN agent A on(A.Agent_Number = P.prop_Agent_Number)
            WHERE Agent_Number = "{}"
            """.format(agentNumber)

        print(sql7)

        mycursor.execute(sql7)
        areas = mycursor.fetchall()
        print(areas)
        headings = ("Property Title", "Property Price")
    return render_template('reviews.html', reviews=areas, headings=headings)


if __name__ == "__main__":
    app.run(debug=True)
