import mysql.connector,sys
import datetime
from mysql.connector import Error
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from random import randint

app = Flask(__name__)

@app.route('/')
def renderLoginPage():
    return render_template('login.html')


@app.route('/login', methods = ['POST'])
def verifyAndRenderRespective():
	username = request.form['username']
	password = request.form['password']

	try:
		if username == 'cashier' and password == 'cashier123':

			res = runQuery('call delete_old()')
			return render_template('cashier.html')

		elif username == 'manager' and password == 'Password@123':

			res = runQuery('call delete_old()')
			return render_template('manager.html')

		else:
			return render_template('loginfail.html')
	except Exception as e:
		print(e)
		return render_template('loginfail.html')


# Routes for cashier
@app.route('/getMoviesShowingOnDate', methods = ['POST'])
def moviesOnDate():
	date = request.form['date']

	res = runQuery("SELECT DISTINCT movie_id,movie_name,type FROM movies NATURAL JOIN shows WHERE Date = '"+date+"'")

	if res == []:
		return '<h4>No Movies Showing</h4>'
	else:
		return render_template('movies.html',movies = res)


@app.route('/getTimings', methods = ['POST'])
def timingsForMovie():
	date = request.form['date']
	movieID = request.form['movieID']
	movieType = request.form['type']

	res = runQuery("SELECT time FROM shows WHERE Date='"+date+"' and movie_id = "+movieID+" and type ='"+movieType+"'")
	
	list = []

	for i in res:
		list.append( (i[0], int(i[0]/100), i[0]%100 if i[0]%100 != 0 else '00' ) )

	return render_template('timings.html',timings = list) 


@app.route('/getShowID', methods = ['POST'])
def getShowID():
	date = request.form['date']
	movieID = request.form['movieID']
	movieType = request.form['type']
	time = request.form['time']

	res = runQuery("SELECT show_id FROM shows WHERE Date='"+date+"' and movie_id = "+movieID+" and type ='"+movieType+"' and time = "+time)
	return jsonify({"showID" : res[0][0]})


@app.route('/getAvailableSeats', methods = ['POST'])
def getSeating():
	showID = request.form['showID']

	res = runQuery("SELECT class,no_of_seats FROM shows NATURAL JOIN halls WHERE show_id = "+showID)

	totalGold = 0
	totalStandard = 0

	for i in res:
		if i[0] == 'gold':
			totalGold = i[1]
		if i[0] == 'standard':
			totalStandard = i[1]

	res = runQuery("SELECT seat_no FROM booked_tickets WHERE show_id = "+showID)

	goldSeats = []
	standardSeats = []

	for i in range(1, totalGold + 1):
		goldSeats.append([i,''])

	for i in range(1, totalStandard + 1):
		standardSeats.append([i,''])

	for i in res:
		if i[0] > 1000:
			goldSeats[ i[0] % 1000 - 1 ][1] = 'disabled'
		else:
			standardSeats[ i[0] - 1 ][1] = 'disabled'

	return render_template('seating.html', goldSeats = goldSeats, standardSeats = standardSeats)


@app.route('/getPrice', methods = ['POST'])
def getPriceForClass():
	showID = request.form['showID']
	seatClass = request.form['seatClass']

	res = runQuery("INSERT INTO halls VALUES(-1,'-1',-1)");

	res = runQuery("DELETE FROM halls WHERE hall_id = -1")

	res = runQuery("SELECT price FROM shows NATURAL JOIN price_listing WHERE show_id = "+showID)

	if res == []:
		return '<h5>Prices Have Not Been Assigned To This Show, Please Try Again Later!</h5>'

	price = int(res[0][0])
	if seatClass == 'gold':
		price = price * 1.5

	return '<h5>Ticket Price: $ '+str(price)+'</h5>\
	<button onclick="confirmBooking()" class="btn-warning">Confirm Booking</button>'


@app.route('/insertBooking', methods = ['POST'])
def createBooking():
	showID = request.form['showID']
	seatNo = request.form['seatNo']
	seatClass = request.form['seatClass']

	if seatClass == 'gold':
		seatNo = int(seatNo) + 1000

	ticketNo = 0
	res = None

	while res != []:
		ticketNo = randint(0, 2147483646)
		res = runQuery("SELECT ticket_no FROM booked_tickets WHERE ticket_no = "+str(ticketNo))
	
	res = runQuery("INSERT INTO booked_tickets VALUES("+str(ticketNo)+","+showID+","+str(seatNo)+")")

	if res == []:
		return '<h5>Ticket Has Been Booked Successfully!</h5>\
		<h6>Ticket Number: '+str(ticketNo)+'</h6>'


# Routes for manager
@app.route('/getShowsShowingOnDate', methods = ['POST'])
def getShowsOnDate():
	date = request.form['date']

	res = runQuery("SELECT show_id,movie_name,type,time FROM shows NATURAL JOIN movies WHERE Date = '"+date+"'")
	
	if res == []:
		return '<h4>No Shows Showing</h4>'
	else:
		shows = []
		for i in res:
			x = i[3] % 100
			if i[3] % 100 == 0:
				x = '00'
			shows.append([ i[0], i[1], i[2], int(i[3] / 100), x ])

		return render_template('shows.html', shows = shows)


@app.route('/getBookedWithShowID', methods = ['POST'])
def getBookedTickets():
	showID = request.form['showID']

	res = runQuery("SELECT ticket_no,seat_no FROM booked_tickets WHERE show_id = "+showID+" order by seat_no")

	if res == []:
		return '<h5>No Bookings!!</h5>'

	tickets = []
	for i in res:
		if i[1] > 1000:
			tickets.append([i[0], i[1] - 1000, 'Gold'])
		else:
			tickets.append([i[0], i[1], 'Standard'])

	return render_template('bookedtickets.html', tickets = tickets)


@app.route('/fetchMovieInsertForm', methods = ['GET'])
def getMovieForm():
	return render_template('movieform.html')


@app.route('/insertMovie', methods = ['POST'])
def insertMovie():
	movieName = request.form['movieName']
	movieLen = request.form['movieLen']
	movieLang = request.form['movieLang']
	types = request.form['types']
	startShowing = request.form['startShowing']
	endShowing = request.form['endShowing']

	res = runQuery('SELECT * FROM movies')

	for i in res:
		if i[1] == movieName and i[2] == int(movieLen) and i[3] == movieLang \
		 and i[4].strftime('%Y/%m/%d') == startShowing and i[5].strftime('%Y/%m/%d') == endShowing:
			return '<h5>The Same Movie Already Exists</h5>'

	movieID = 0
	res = None

	while res != []:
		movieID = randint(0, 2147483646)
		res = runQuery("SELECT movie_id FROM movies WHERE movie_id = "+str(movieID))
	
	res = runQuery("INSERT INTO movies VALUES("+str(movieID)+",'"+movieName+"',"+movieLen+\
		",'"+movieLang+"','"+startShowing+"','"+endShowing+"')")

	if res == []:
		print("Was able to add movie")
		subTypes = types.split(' ')

		while len(subTypes) < 3:
			subTypes.append('NUL')

		res = runQuery("INSERT INTO types VALUES("+str(movieID)+",'"+subTypes[0]+"','"+subTypes[1]+"','"+subTypes[2]+"')")

		if res == []:
			return '<h5>Movie Added Successfully!</h5>\
			<h6>Movie ID: '+str(movieID)+'</h6>'
		else:
			print(res)
	else:
		print(res)

	return '<h5>Something Went Wrong</h5>'


@app.route('/getValidMovies', methods = ['POST'])
def validMovies():
	showDate = request.form['showDate']

	res = runQuery("SELECT movie_id,movie_name,length,language FROM movies WHERE show_start <= '"+showDate+\
		"' and show_end >= '"+showDate+"'")

	if res == []:
		return '<h5>No Movies Available for Showing On Selected Date</h5>'

	movies = []

	for i in res:
		subTypes = runQuery("SELECT * FROM types WHERE movie_id = "+str(i[0]) )

		t = subTypes[0][1]

		if subTypes[0][2] != 'NUL':
			t = t + ' ' + subTypes[0][2]
		if subTypes[0][3] != 'NUL':
			t = t + ' ' + subTypes[0][3]

		movies.append( (i[0],i[1],t,i[2],i[3]) )

	return render_template('validmovies.html', movies = movies)


@app.route('/getHallsAvailable', methods = ['POST'])
def getHalls():
	movieID = request.form['movieID']
	showDate = request.form['showDate']
	showTime = request.form['showTime']

	res = runQuery("SELECT length FROM movies WHERE movie_id = "+movieID)

	movieLen = res[0][0]

	showTime = int(showTime)

	showTime = int(showTime / 100)*60 + (showTime % 100)

	endTime = showTime + movieLen 

	res = runQuery("SELECT hall_id, length, time FROM shows NATURAL JOIN movies WHERE Date = '"+showDate+"'")

	unavailableHalls = set()

	for i in res:

		x = int(i[2] / 100)*60 + (i[2] % 100)

		y = x + i[1]

		if x >= showTime and x <= endTime:
			unavailableHalls = unavailableHalls.union({i[0]})

		if y >= showTime and y <= endTime:
			unavailableHalls = unavailableHalls.union({i[0]})

	res = runQuery("SELECT DISTINCT hall_id FROM halls")

	availableHalls = set()

	for i in res:

		availableHalls = availableHalls.union({i[0]})

	availableHalls = availableHalls.difference(unavailableHalls)

	if availableHalls == set():

		return '<h5>No Halls Available On Given Date And Time</h5>'

	return render_template('availablehalls.html', halls = availableHalls)
	

@app.route('/insertShow', methods = ['POST'])
def insertShow():
	hallID = request.form['hallID']
	movieID = request.form['movieID']
	movieType = request.form['movieType']
	showDate = request.form['showDate']
	showTime = request.form['showTime']

	showID = 0
	res = None

	while res != []:
		showID = randint(0, 2147483646)
		res = runQuery("SELECT show_id FROM shows WHERE show_id = "+str(showID))
	
	res = runQuery("INSERT INTO shows VALUES("+str(showID)+","+movieID+","+hallID+\
		",'"+movieType+"',"+showTime+",'"+showDate+"',"+'NULL'+")")

	print(res)

	if res == []:
		return '<h5>Show Scheduled Successfully</h5>\
		<h6>Show ID: '+str(showID)+'</h6>'

	else:
		print(res)
	return '<h5>Something Went Wrong!!</h5>'


@app.route('/getPriceList', methods = ['GET'])
def priceList():
	res = runQuery("SELECT * FROM price_listing ORDER BY type")

	sortedDays = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']

	res = sorted( res, key = lambda x : sortedDays.index(x[2]) )

	return render_template('currentprices.html', prices = res)


@app.route('/setNewPrice', methods = ['POST'])
def setPrice():
	priceID = request.form['priceID']
	newPrice = request.form['newPrice']

	res = runQuery("UPDATE price_listing SET price = "+str(newPrice)+" WHERE price_id = "+str(priceID))

	if res == []:
		return '<h5>Price Updated Successfully</h5>\
			<h6>Standard: $ '+newPrice+'</h6>\
			<h6>Gold: $ '+str( int(int(newPrice) * 1.5) )+'</h6>'

	else:
		print(res)
	return '<h5>Something Went Wrong!!</h5>'


@app.route('/showAllMovies', methods=['GET'])
def showAllMovies():
    # Truy vấn tất cả các phim từ bảng movies
    res = runQuery("SELECT movie_id, movie_name, length, language, show_start, show_end FROM movies")
    
    # Nếu không có phim nào trong cơ sở dữ liệu
    if not res:
        return '<h5>No Movies Found</h5>'
    
    # Tạo danh sách các phim để gửi đến template
    movies = []
    for movie in res:
        movies.append({
            'movie_id': movie[0],
            'movie_name': movie[1],
            'length': movie[2],
            'language': movie[3],
            'show_start': movie[4].strftime('%Y-%m-%d'),
            'show_end': movie[5].strftime('%Y-%m-%d')
        })
    
    # Render template allmovies.html với danh sách các phim
    return render_template('allmovies.html', movies=movies)
@app.route('/deleteMovie', methods=['POST'])
def deleteMovie():
    movie_id = request.form['movie_id']
    
    # Xóa phim từ bảng movies dựa vào movie_id
    res = runQuery(f"DELETE FROM movies WHERE movie_id = {movie_id}")
    
    if res == []:
        return 'Movie deleted successfully'
    else:
        return 'Error deleting movie', 500

@app.route('/allMovies', methods=['GET', 'POST'])
def allMovies():
    # Hiển thị danh sách phim
    if request.method == 'GET':
        movies = runQuery("SELECT movie_id, movie_name, length, language, show_start, show_end FROM movies")
        return render_template('allmovies.html', movies=movies)
    
    # Xử lý khi người dùng muốn chỉnh sửa một phim
    if request.method == 'POST':
        # Lấy movie_id từ form
        movie_id = request.form.get('movie_id')

        # Nếu không có movie_id thì trả về lỗi
        if not movie_id:
            return '<h5>Error: Movie ID not provided</h5>', 400

        # Truy vấn thông tin phim cần chỉnh sửa
        res = runQuery(f"SELECT movie_id, movie_name, length, language, show_start, show_end FROM movies WHERE movie_id = {movie_id}")
        if not res:
            return '<h5>Movie Not Found</h5>'

        # Thông tin phim để hiển thị form chỉnh sửa
        movie = {
            'movie_id': res[0][0],
            'movie_name': res[0][1],
            'length': res[0][2],
            'language': res[0][3],
            'show_start': res[0][4].strftime('%Y-%m-%d'),
            'show_end': res[0][5].strftime('%Y-%m-%d')
        }

        # Lấy danh sách phim và thêm form chỉnh sửa bên dưới
        movies = runQuery("SELECT movie_id, movie_name, length, language, show_start, show_end FROM movies")
        return render_template('allmovies.html', movies=movies, edit_movie=movie)

    
@app.route('/editMovie', methods=['POST'])
def editMovie():
    # Lấy thông tin từ form
    movie_id = request.form.get('movie_id')
    movie_name = request.form.get('movie_name')
    length = request.form.get('length')
    language = request.form.get('language')
    show_start = request.form.get('show_start')
    show_end = request.form.get('show_end')

    # Kiểm tra dữ liệu
    if not all([movie_id, movie_name, length, language, show_start, show_end]):
        return '<h5>Error: Missing data</h5>', 400

    # Cập nhật thông tin phim trong cơ sở dữ liệu
    update_query = f"""
        UPDATE movies
        SET movie_name = '{movie_name}',
            length = {length},
            language = '{language}',
            show_start = '{show_start}',
            show_end = '{show_end}'
        WHERE movie_id = {movie_id}
    """
    runQuery(update_query)

    # Trả về một thông báo thành công
    return 'Success', 200





@app.route('/showAllTickets')
def show_all_tickets():
        # Truy vấn tất cả các vé từ bảng booked_tickets
        res = runQuery("""
            SELECT bt.ticket_no, s.show_id, s.time, m.movie_name, bt.seat_no 
            FROM booked_tickets bt
            INNER JOIN shows s ON bt.show_id = s.show_id
            INNER JOIN movies m ON s.movie_id = m.movie_id
        """)
        
        # Nếu không có vé nào trong cơ sở dữ liệu
        if not res:
            return '<h5>No Tickets Found</h5>'
        
        # Tạo danh sách vé để gửi đến template
        tickets = []
        for ticket in res:
            tickets.append({
                'ticket_no': ticket[0],
                'show_id': ticket[1],
                'time': ticket[2],
                'movie_name': ticket[3],
                'seat_no': ticket[4]
            })
        
        return render_template('alltickets.html', tickets=tickets)
    
@app.route('/deleteTicket', methods=['POST'])
def delete_ticket():
    ticket_no = request.form['ticket_no']
    
    # Xóa phim từ bảng movies dựa vào movie_id
    res = runQuery(f"DELETE FROM booked_tickets WHERE ticket_no = {ticket_no}")
    
    if res == []:
        return 'Ticket deleted successfully'
    else:
        return 'Error deleting ticket', 500

@app.route('/showAllShows')
def show_all_shows():
    # Truy vấn tất cả các show từ bảng shows và lấy tên phim từ bảng movies
    res = runQuery("""
        SELECT s.show_id, m.movie_name, s.hall_id, s.type, s.time, s.date
        FROM shows s
        INNER JOIN movies m ON s.movie_id = m.movie_id
    """)
    
    # Nếu không có show nào trong cơ sở dữ liệu
    if not res:
        return '<h5>No Shows Found</h5>'
    
    # Tạo danh sách các show để gửi đến template
    shows = []
    for show in res:
        shows.append({
            'show_id': show[0],
            'movie_name': show[1],
            'hall_id': show[2],
            'type': show[3],
            'time': show[4],
            'date': show[5]
        })
    
    return render_template('allshow.html', shows=shows)


@app.route('/deleteShow', methods=['POST'])
def delete_show():
    show_id = request.form['show_id']
    
    # Xóa show từ bảng shows dựa vào show_id
    res = runQuery(f"DELETE FROM shows WHERE show_id = {show_id}")
    
    if not res:
        return 'Show deleted successfully'
    else:
        return 'Error deleting show', 500



def runQuery(query):
	try:
		db = mysql.connector.connect(
			host='localhost',
			database='dbtheatre',
			user='root',
			password='')

		if db.is_connected():
			print("Connected to MySQL, running query: ", query)
			cursor = db.cursor(buffered = True)
			cursor.execute(query)
			db.commit()
			res = None
			try:
				res = cursor.fetchall()
			except Exception as e:
				print("Query returned nothing, ", e)
				return []
			return res

	except Exception as e:
		print(e)
		return e

	finally:
		db.close()

	print("Couldn't connect to MySQL Database")
    #Couldn't connect to MySQL
	return None


if __name__ == "__main__":
    app.run(host='0.0.0.0')
 
