
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session
import re

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'aSDF2134!@#supersecretkey'

DATABASE_USERNAME = ""
DATABASE_PASSWRD = ""
DATABASE_HOST = "34.148.223.31"
DATABASEURI = "postgresql://my2903:770042@34.148.223.31/proj1part2"

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route('/')
def index():
    print(request.args)
    select_query = "SELECT name from test"
    cursor = g.conn.execute(text(select_query))
    names = [result[0] for result in cursor]
    cursor.close()
    context = dict(data=names)
    return render_template("index.html", **context)

@app.route('/another')
def another():
    return render_template("another.html")

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    params = {"new_name": name}
    g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
    g.conn.commit()
    return redirect('/')

@app.route('/login')
def login():
    abort(401)

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET':
        form_data = session.get('form_data', {})  
        return render_template('create_user.html', **form_data)
    elif request.method == 'POST':
        country = request.form['country']
        city_name = request.form['city_name']
        email = request.form['email']

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            return "Invalid email format. Please go back and enter a valid email.", 400

        phone = request.form.get('phone')
        phone_regex = r'^(?:\+1\d{10}|\+86\d{11})$'
        if not re.match(phone_regex, phone):
            return "Please enter a valid US or China phone number (e.g., +11234567890 or +8613812345678)", 400

        existing_user = g.conn.execute(text("""
            SELECT 1 FROM Users WHERE email = :email AND phone = :phone
        """), {'email': email, 'phone': phone}).fetchone()
        if existing_user:
            return "This user (email + phone) is already registered. Please use another one or go to sign in.", 400

        result = g.conn.execute(text("""
            SELECT city_id FROM City
            WHERE country ILIKE :country AND city_name ILIKE :city_name
        """), {'country': country, 'city_name': city_name})
        city_row = result.fetchone()
        if city_row is None:
            return "City not found", 400
        city_id = city_row[0]

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['date_of_birth']
        gender = request.form['gender']
        preferred_travel_type = request.form.get('preferred_travel_type', '')
        occupation = request.form.get('occupation', '')
        income = request.form.get('income', '')

        session['form_data'] = {
            'country': country,
            'city_name': city_name,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': dob,
            'gender': gender,
            'preferred_travel_type': preferred_travel_type,
            'occupation': occupation,
            'income': income
        }

        params = {
            "city_id": city_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob,
            "gender": gender,
            "preferred_travel_type": preferred_travel_type,
            "occupation": occupation,
            "income": income
        }

        try:
            result = g.conn.execute(text("""
                INSERT INTO Users (city_id, email, first_name, last_name, date_of_birth, gender, preferred_travel_type, occupation, income)
                VALUES (:city_id, :email, :first_name, :last_name, :date_of_birth, :gender, :preferred_travel_type, :occupation, :income)
                RETURNING user_id
            """), params)
            user_id = result.fetchone()[0]
            session['user_id'] = user_id
            g.conn.commit()
            return redirect('/create_trip')
        except Exception as e:
            g.conn.rollback()
            return f"Error: {str(e)}", 400

    return render_template('create_user.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        user = g.conn.execute(text("""
            SELECT user_id FROM Users WHERE email = :email AND phone = :phone
        """), {'email': email, 'phone': phone}).fetchone()
        if user:
            session['user_id'] = user.user_id
            return redirect('/create_trip')
        else:
            return "User not found. Please register.", 400
    return render_template('sign_in.html')

@app.route('/create_trip', methods=['GET', 'POST'])
def create_trip():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/create_user')

        result = g.conn.execute(text("""
            SELECT city_id FROM Users WHERE user_id = :user_id
        """), {'user_id': user_id})
        row = result.fetchone()
        if row is None:
            return "User city not found.", 400
        origin = row[0]

        begin_date = request.form['begin_date']
        end_date = request.form['end_date']
        num_adults = request.form['num_adults']
        num_children = request.form['num_children']
        
        session['trip_form_data'] = {
            'begin_date': begin_date,
            'end_date': end_date,
            'num_adults': num_adults,
            'num_children': num_children
        }


        params = {
            'begin_date': begin_date,
            'end_date': end_date,
            'origin': origin,
            'num_adults': num_adults,
            'num_children': num_children
        }

        result = g.conn.execute(text("""
            INSERT INTO Trip (begin_date, end_date, origin, num_adults, num_children)
            VALUES (:begin_date, :end_date, :origin, :num_adults, :num_children)
            RETURNING trip_id
        """), params)
        trip_id = result.fetchone()[0]

        g.conn.execute(text("""
            INSERT INTO User_Trip (user_id, trip_id)
            VALUES (:user_id, :trip_id)
        """), {'user_id': user_id, 'trip_id': trip_id})

        session['trip_id'] = trip_id
        g.conn.commit()
        return redirect('/trip_details')

    form_data = session.get('trip_form_data', {})
    return render_template('create_trip.html', **form_data)


@app.route('/trip_details', methods=['GET', 'POST'])
def trip_details():
    trip_id = session.get('trip_id')
    user_id = session.get('user_id')  

    if not trip_id or not user_id:
        return "Missing trip or user info in session", 400

    if request.method == 'POST':
        action = request.form.get('action')

        # insert Party Members
        nicknames = request.form.getlist('nickname')
        ages = request.form.getlist('age_at_travel')
        genders = request.form.getlist('gender')
        relations = request.form.getlist('relationship_to_user')

        for nickname, age, gender, relation in zip(nicknames, ages, genders, relations):
            if not gender:  # 防止违反 NOT NULL constraint
                continue  # 或 return 错误提示
            g.conn.execute(text("""
                INSERT INTO Party_Member (user_id, trip_id, nickname, age_at_travel, gender, relationship_to_user)
                VALUES (:user_id, :trip_id, :nickname, :age, :gender, :relation)
            """), {
                'user_id': user_id,
                'trip_id': trip_id,
                'nickname': nickname,
                'age': age if age else None,
                'gender': gender,
                'relation': relation
            })

        # Get Experience fields
        exp_names = request.form.getlist('experience_name')
        exp_cats = request.form.getlist('experience_category')
        exp_park_ids = request.form.getlist('experience_park_id')
        exp_times = request.form.getlist('purchase_time')
        pay_methods = request.form.getlist('payment_method')
        exp_costs = request.form.getlist('experience_cost')  # <- ✅ ADD HERE

        for name, cat, park_id, time, method, cost in zip(exp_names, exp_cats, exp_park_ids, exp_times, pay_methods, exp_costs):
            result = g.conn.execute(text("""
                INSERT INTO Experience (name, category, park_id)
                VALUES (:name, :cat, :park_id)
                ON CONFLICT (name, park_id) DO NOTHING
                RETURNING experience_id
            """), {'name': name, 'cat': cat, 'park_id': park_id})

            experience_id = result.fetchone()
            if not experience_id:
                experience_id = g.conn.execute(text("""
                    SELECT experience_id FROM Experience
                    WHERE name = :name AND park_id = :park_id
                """), {'name': name, 'park_id': park_id}).fetchone()

            experience_id = experience_id[0]

            g.conn.execute(text("""
                INSERT INTO Has_Experience (trip_id, experience_id, park_id, purchase_time, payment_method, cost)
                VALUES (:trip_id, :experience_id, :park_id, :time, :method, :cost)
                ON CONFLICT DO NOTHING
            """), {
                'trip_id': trip_id,
                'experience_id': experience_id,
                'park_id': park_id,
                'time': time,
                'method': method,
                'cost': cost
            })
        
        # Get Hotel fields
        hotel_names = request.form.getlist('hotel_name')
        hotel_types = request.form.getlist('hotel_type')
        room_types = request.form.getlist('room_type')
        nights_list = request.form.getlist('nights_stayed')
        hotel_costs = request.form.getlist('hotel_cost')

        for name, htype, rtype, nights, cost in zip(hotel_names, hotel_types, room_types, nights_list, hotel_costs):
            if not name or not htype or not rtype:
                continue  # 如果这组数据没有填完，就跳过这一组
            
            g.conn.execute(text("""
                INSERT INTO Hotel_Stay (
                    trip_id, hotel_name, hotel_type, room_type, nights_stayed, hotel_cost
                ) VALUES (
                    :trip_id, :hotel_name, :hotel_type, :room_type, :nights, :cost
                )
            """), {
                'trip_id': trip_id,
                'hotel_name': name,
                'hotel_type': htype,
                'room_type': rtype,
                'nights': int(nights) if nights else None,
                'cost': float(cost) if cost else None
            })
        
        # Insert Dining Experiences
        rest_names = request.form.getlist('restaurant_name')
        meal_types = request.form.getlist('meal_type')
        park_ids = request.form.getlist('restaurant_park_id')
        meal_times = request.form.getlist('meal_time')
        meal_costs = request.form.getlist('meal_cost')

        for rname, mtype, pid, mtime, mcost in zip(rest_names, meal_types, park_ids, meal_times, meal_costs):
            if not rname or not mtype or not pid or not mtime:
                continue  # 防御性处理
            
            g.conn.execute(text("""
                INSERT INTO Dining_Experience (trip_id, restaurant_name, meal_type, park_id, meal_time, meal_cost)
                VALUES (:trip_id, :rname, :mtype, :pid, :mtime, :mcost)
            """), {
                'trip_id': trip_id,
                'rname': rname,
                'mtype': mtype,
                'pid': pid,
                'mtime': mtime,
                'mcost': float(mcost) if mcost else None
            })
        

        # Inssert Experience
        exp_names = request.form.getlist('experience_name')
        exp_cats = request.form.getlist('experience_category')
        exp_park_ids = request.form.getlist('experience_park_id')
        exp_times = request.form.getlist('purchase_time')
        pay_methods = request.form.getlist('payment_method')
        exp_costs = request.form.getlist('experience_cost')

        for name, cat, park_id, time, method, cost in zip(exp_names, exp_cats, exp_park_ids, exp_times, pay_methods, exp_costs):
            if not name or not cat or not park_id:
                continue
       
            # 插入 Experience 表（如果不存在）
            result = g.conn.execute(text("""
                INSERT INTO Experience (name, category, park_id)
                VALUES (:name, :cat, :park_id)
                ON CONFLICT (name, park_id) DO NOTHING
                RETURNING experience_id
            """), {'name': name, 'cat': cat, 'park_id': park_id})

            experience_id = result.fetchone()
            if not experience_id:
                experience_id = g.conn.execute(text("""
                    SELECT experience_id FROM Experience
                    WHERE name = :name AND park_id = :park_id
                """), {'name': name, 'park_id': park_id}).fetchone()

            experience_id = experience_id[0]

            # 插入 Has_Experience（关联本次 trip）
            g.conn.execute(text("""
                INSERT INTO Has_Experience (trip_id, experience_id, park_id, purchase_time, payment_method, cost)
                VALUES (:trip_id, :experience_id, :park_id, :time, :method, :cost)
                ON CONFLICT DO NOTHING
            """), {
                'trip_id': trip_id,
                'experience_id': experience_id,
                'park_id': park_id,
                'time': time,
                'method': method,
                'cost': cost
            })

            # ✅ 插入 Ticket Cost
            ticket_costs = request.form.getlist('ticket_cost')  # HTML表单中的name
            ticket_times = request.form.getlist('ticket_time')  # HTML表单中的name

            for cost, time in zip(ticket_costs, ticket_times):
                if cost and time:
                    g.conn.execute(text("""
                        INSERT INTO ticket_cost (trip_id, cost, transaction_time)
                        VALUES (:trip_id, :cost, :time)
                    """), {
                        'trip_id': trip_id,
                        'cost': float(cost),
                        'time': time
                    })


            g.conn.commit()

            if action == 'save':
                return "Saved! You can come back later."
            elif action == 'submit':
                session.pop('user_id', None)
                session.pop('trip_id', None)
                return render_template('submission_success.html')

    return render_template('trip_details.html')

@app.route('/view_trips')
def view_trips():
    result = g.conn.execute(text("""
        SELECT
            u.user_id,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.date_of_birth)) AS age,
            u.occupation,
            c.city_name,
            c.country,
            t.trip_id,
            t.begin_date,
            t.end_date,
            t.num_adults,
            t.num_children,
            (t.num_adults + t.num_children) AS group_size                   
        FROM Users u
        JOIN City c ON u.city_id = c.city_id
        JOIN User_Trip ut ON u.user_id = ut.user_id
        JOIN Trip t ON ut.trip_id = t.trip_id
        ORDER BY t.trip_id DESC
    """))
    trips = result.fetchall()

    # 查询对应的 trip_id 的详细信息
    details_result = g.conn.execute(text("""
        SELECT 'dining' AS entry_type,
               trip_id::TEXT,
               restaurant_name AS name,
               meal_type AS category,
               park_id::TEXT,
               meal_time::TEXT AS datetime,
               meal_cost::TEXT AS cost
        FROM Dining_Experience

        UNION ALL

        SELECT 'hotel',
               trip_id::TEXT,
               hotel_name,
               room_type,
               NULL,
               nights_stayed::TEXT,
               hotel_cost::TEXT
        FROM Hotel_Stay

        UNION ALL

        SELECT 'ticket',
               trip_id::TEXT,
               NULL,
               NULL,
               NULL,
               transaction_time::TEXT,
               cost::TEXT
        FROM Ticket_Cost

        UNION ALL
        
        SELECT 'experience',
                he.trip_id::TEXT,
                e.name,
                e.category,
                e.park_id::TEXT,
                he.purchase_time::TEXT,
                he.cost::TEXT
        FROM Has_Experience he
        JOIN Experience e ON he.experience_id = e.experience_id
    """))


    detail_map = {}
    for row in details_result:
        trip_id = row.trip_id
        if trip_id not in detail_map:
            detail_map[trip_id] = []
        detail_map[trip_id].append(row)

    # 🔹 汇总酒店花费
    hotel_costs = g.conn.execute(text("""
        SELECT trip_id, SUM(hotel_cost) AS total_hotel_cost
        FROM Hotel_Stay
        GROUP BY trip_id
    """)).fetchall()
    hotel_cost_map = {row.trip_id: row.total_hotel_cost for row in hotel_costs}

    # 🔹 统计 party adults / children 数量
    party_counts = g.conn.execute(text("""
        SELECT trip_id,
               SUM(CASE WHEN age_at_travel < 18 THEN 1 ELSE 0 END) AS children,
               SUM(CASE WHEN age_at_travel >= 18 THEN 1 ELSE 0 END) AS adults
        FROM Party_Member
        GROUP BY trip_id
    """)).fetchall()
    party_map = {row.trip_id: {"adults": row.adults, "children": row.children} for row in party_counts}

    # 🍽️ Dining 费用聚合
    dining_costs = g.conn.execute(text("""
        SELECT trip_id, SUM(meal_cost) AS total_dining
        FROM Dining_Experience
        GROUP BY trip_id
    """)).fetchall()
    dcost_map = {row.trip_id: row.total_dining for row in dining_costs}


    # 🔹 Experience 花费
    exp_costs = g.conn.execute(text("""
        SELECT trip_id, SUM(cost) AS total_exp
        FROM Has_Experience
        GROUP BY trip_id
    """)).fetchall()
    exp_map = {row.trip_id: row.total_exp for row in exp_costs}

    # 🔹 Ticket 花费
    ticket_costs = g.conn.execute(text("""
        SELECT trip_id, SUM(cost) AS total_ticket
        FROM Ticket_Cost
        GROUP BY trip_id
    """)).fetchall()
    ticket_map = {row.trip_id: row.total_ticket for row in ticket_costs}

    # 🔹 Transportation 花费
    trans_costs = g.conn.execute(text("""
        SELECT trip_id, SUM(cost) AS total_trans
        FROM Transportation_Cost
        GROUP BY trip_id
    """)).fetchall()
    trans_map = {row.trip_id: row.total_trans for row in trans_costs}

    # 💰 计算 total cost per trip
    from decimal import Decimal

    total_cost_map = {
        trip_id: (
            (hotel_cost_map.get(trip_id) or Decimal('0.00')) +
            (dcost_map.get(trip_id) or Decimal('0.00')) +
            (ticket_map.get(trip_id) or Decimal('0.00')) +
            (exp_map.get(trip_id) or Decimal('0.00')) +
            (trans_map.get(trip_id) or Decimal('0.00'))
        )
        for trip_id in set().union(hotel_cost_map, dcost_map, ticket_map, exp_map, trans_map)
    }


    # 💡 计算四分位阈值
    cost_values = sorted(total_cost_map.values())
    n = len(cost_values)
    q1 = cost_values[n // 4] if n >= 4 else 0
    q2 = cost_values[n // 2] if n >= 2 else 0
    q3 = cost_values[(3 * n) // 4] if n >= 4 else 0

    # 🔢 按照 cost 分组
    grouped_users = {1: [], 2: [], 3: [], 4: []}
    for trip in trips:
        trip_id = trip.trip_id
        cost = total_cost_map.get(trip_id, 0)

        if cost <= q1:
            grouped_users[1].append(trip)
        elif cost <= q2:
            grouped_users[2].append(trip)
        elif cost <= q3:
            grouped_users[3].append(trip)
        else:
            grouped_users[4].append(trip)
    
    # 👇 渲染 HTML
    return render_template("view_trips.html",
        trips=trips,
        details=detail_map,
        hotel_cost_map=hotel_cost_map,
        party_map=party_map,
        exp_map=exp_map,
        ticket_map=ticket_map,
        trans_map=trans_map,
        dcost_map=dcost_map,
        total_cost_map=total_cost_map,
        grouped_users=grouped_users
    )

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()


