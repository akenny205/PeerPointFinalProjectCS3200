########################################################
# Sample customers blueprint of endpoints
# Remove this file if you are not using it in your project
########################################################
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db
from datetime import datetime

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of routes.
users = Blueprint('users', __name__)


#------------------------------------------------------------
# Get all users from the system [system admin purposes] - Done
@users.route('/user', methods=['GET'])
def get_customers():
    advisor_id = request.args.get('advisor_id')
    cursor = db.get_db().cursor()
    
    if advisor_id:
        query = '''SELECT UserID, fname, lname, joinDate, Usertype 
                   FROM users WHERE AdminID = %s'''
        cursor.execute(query, (advisor_id,))
    else:
        query = '''SELECT UserID, fname, lname, joinDate, Usertype FROM users'''
        cursor.execute(query)
    
    theData = cursor.fetchall()
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

#------------------------------------------------------------
# Get users either mentors or mentees with optional filtering - Done
@users.route('/user/type', methods=['GET'])
def get_users_by_type():
    user_type = request.args.get('usertype')
    # Get optional filter parameters
    interest = request.args.get('interest')
    skill = request.args.get('skill')
    career_goal = request.args.get('career_goal')
    career_path = request.args.get('career_path')
    
    cursor = db.get_db().cursor()
    
    # Base query
    query = '''SELECT DISTINCT u.UserID, u.fname, u.lname, u.joinDate 
               FROM users u'''
    conditions = ['u.Usertype = %s']
    params = [user_type]
    
    # Add joins and conditions based on filters
    if interest:
        query += ' JOIN interests i ON u.UserID = i.UserID'
        conditions.append('i.Interest = %s')
        params.append(interest)
    
    if skill:
        query += ' JOIN skills s ON u.UserID = s.UserID'
        conditions.append('s.Skill = %s')
        params.append(skill)
    
    if career_goal:
        query += ' JOIN career_goals g ON u.UserID = g.UserID'
        conditions.append('g.Goal = %s')
        params.append(career_goal)
    
    if career_path:
        query += ' JOIN career_path p ON u.UserID = p.UserID'
        conditions.append('p.CareerPath = %s')
        params.append(career_path)
    
    # Add WHERE clause
    query += ' WHERE ' + ' AND '.join(conditions)
    
    cursor.execute(query, tuple(params))
    theData = cursor.fetchall()
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

#------------------------------------------------------------
# Get users alumni
@users.route('/user/alumni', methods=['GET'])
def get_alumni():
    cursor = db.get_db().cursor()
    query = '''SELECT UserID, fname, lname, joinDate FROM users WHERE Status = FALSE'''
    cursor.execute(query)
    theData = cursor.fetchall()
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

#------------------------------------------------------------
# Get count of all users by type [system admin purposes]
@users.route('/user/count', methods=['GET'])
def get_users_count():
    cursor = db.get_db().cursor()
    query = '''SELECT Usertype, COUNT(*) AS Count FROM users GROUP BY Usertype'''
    cursor.execute(query)
    theData = cursor.fetchall()
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

#------------------------------------------------------------
# Add new users to the system [system admin / advisor purposes]
@users.route('/user/add', methods=['POST'])
def add_user():
    user_info = request.json
    query = '''INSERT INTO users (fname, lname, Usertype, Email, Phone, Major, Minor, AdminID, EmpID)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    data = (
        user_info['fname'], user_info['lname'], user_info['usertype'], user_info['email'], 
        user_info['phone'], user_info['major'], user_info['minor'], user_info['admin_id'], 
        user_info.get('emp_id')
    )
    cursor = db.get_db().cursor()
    cursor.execute(query, data)
    db.get_db().commit()
    return 'User added!', 201

#------------------------------------------------------------
# Get user profile details [users]
@users.route('/user/<userID>', methods=['GET'])
def get_user_profile(userID):
    cursor = db.get_db().cursor()
    
    # Get basic user info
    user_query = '''SELECT fname, lname, Usertype, Email, Phone, Major, Minor, 
                           Semesters, numCoops, Matchstatus
                    FROM users 
                    WHERE UserID = %s'''
    cursor.execute(user_query, (userID,))
    user_data = cursor.fetchone()
    
    if not user_data:
        return 'User not found', 404
        
    # Get user skills
    cursor.execute('SELECT Skill FROM skills WHERE UserID = %s', (userID,))
    skills = [row['Skill'] for row in cursor.fetchall()]
    
    # Get user interests
    cursor.execute('SELECT Interest FROM interests WHERE UserID = %s', (userID,))
    interests = [row['Interest'] for row in cursor.fetchall()]
    
    # Get career goals
    cursor.execute('SELECT Goal FROM career_goals WHERE UserID = %s', (userID,))
    career_goals = [row['Goal'] for row in cursor.fetchall()]
    
    # Get career path
    cursor.execute('SELECT CareerPath FROM career_path WHERE UserID = %s', (userID,))
    career_path = [row['CareerPath'] for row in cursor.fetchall()]

    # Get experiences
    cursor.execute('''SELECT ExperienceName, Date, Location, Description 
                     FROM experience WHERE UserID = %s''', (userID,))
    experiences = [dict(row) for row in cursor.fetchall()]
    
    # Combine all data
    profile_data = {
        'fname': user_data['fname'],
        'lname': user_data['lname'],
        'usertype': user_data['Usertype'],
        'email': user_data['Email'],
        'phone': user_data['Phone'],
        'major': user_data['Major'],
        'minor': user_data['Minor'],
        'semesters': user_data['Semesters'],
        'num_coops': user_data['numCoops'],
        'matchstatus': user_data['Matchstatus'],
        'skills': skills,
        'interests': interests,
        'career_goals': career_goals,
        'career_path': career_path,
        'experiences': experiences
    }
    
    return jsonify(profile_data), 200

#------------------------------------------------------------ Done until here
# Update user profile [users]
@users.route('/user/<userID>', methods=['PUT'])
def update_user_profile(userID):
    try:
        current_app.logger.info(f"Received PUT request for user {userID}")
        user_info = request.json
        current_app.logger.info(f"Request data: {user_info}")
        
        cursor = db.get_db().cursor()
        connection = db.get_db()
        
        # Start transaction
        connection.begin()
        
        try:
            # Update basic user info first
            user_query = '''UPDATE users 
                        SET fname = %s, lname = %s, Usertype = %s, Email = %s, Phone = %s, 
                            Major = %s, Minor = %s, Semesters = %s, numCoops = %s, Matchstatus = %s
                        WHERE UserID = %s'''
            user_data = (
                user_info['fname'], user_info['lname'], user_info['usertype'], 
                user_info['email'], user_info['phone'], user_info['major'], 
                user_info['minor'], user_info['semesters'], user_info['num_coops'],
                user_info['matchstatus'], userID
            )
            cursor.execute(user_query, user_data)
            current_app.logger.info(f"Basic info updated. Rows affected: {cursor.rowcount}")

            # Update skills
            if 'skills' in user_info:
                current_app.logger.info(f"Updating skills: {user_info['skills']}")
                # Delete existing skills
                cursor.execute('DELETE FROM skills WHERE UserID = %s', (userID,))
                # Insert new skills
                for skill in user_info['skills']:
                    if skill.strip():  # Only insert non-empty skills
                        cursor.execute('INSERT INTO skills (UserID, Skill) VALUES (%s, %s)', 
                                    (userID, skill.strip()))
                current_app.logger.info("Skills updated")

            # Update interests
            if 'interests' in user_info:
                current_app.logger.info(f"Updating interests: {user_info['interests']}")
                # Delete existing interests
                cursor.execute('DELETE FROM interests WHERE UserID = %s', (userID,))
                # Insert new interests
                for interest in user_info['interests']:
                    if interest.strip():  # Only insert non-empty interests
                        cursor.execute('INSERT INTO interests (UserID, Interest) VALUES (%s, %s)', 
                                    (userID, interest.strip()))
                current_app.logger.info("Interests updated")

            # Update career goals
            if 'career_goals' in user_info:
                current_app.logger.info(f"Updating career goals: {user_info['career_goals']}")
                cursor.execute('DELETE FROM career_goals WHERE UserID = %s', (userID,))
                for goal in user_info['career_goals']:
                    if goal.strip():
                        cursor.execute('INSERT INTO career_goals (UserID, Goal) VALUES (%s, %s)', 
                                    (userID, goal.strip()))
                current_app.logger.info("Career goals updated")

            # Update career path
            if 'career_path' in user_info:
                current_app.logger.info(f"Updating career path: {user_info['career_path']}")
                cursor.execute('DELETE FROM career_path WHERE UserID = %s', (userID,))
                for path in user_info['career_path']:
                    if path.strip():
                        cursor.execute('INSERT INTO career_path (UserID, CareerPath) VALUES (%s, %s)', 
                                    (userID, path.strip()))
                current_app.logger.info("Career path updated")

            # Update experiences
            if 'experiences' in user_info:
                current_app.logger.info(f"Updating experiences: {user_info['experiences']}")
                cursor.execute('DELETE FROM experience WHERE UserID = %s', (userID,))
                for exp in user_info['experiences']:
                    if exp['ExperienceName'].strip():  # Only insert if there's at least a name
                        # Ensure date is in correct format or set to NULL if empty
                        date_value = exp['Date'] if exp['Date'] else None
                        
                        cursor.execute('''INSERT INTO experience 
                                    (UserID, ExperienceName, Date, Location, Description)
                                    VALUES (%s, %s, %s, %s, %s)''',
                                    (userID, exp['ExperienceName'], date_value, 
                                     exp['Location'], exp['Description']))
                current_app.logger.info("Experiences updated")

            # Commit all changes
            connection.commit()
            current_app.logger.info("All changes committed successfully")

            # Verify updates
            cursor.execute('SELECT * FROM users WHERE UserID = %s', (userID,))
            user_data = cursor.fetchone()
            
            cursor.execute('SELECT Skill FROM skills WHERE UserID = %s', (userID,))
            skills = [row['Skill'] for row in cursor.fetchall()]
            
            cursor.execute('SELECT Interest FROM interests WHERE UserID = %s', (userID,))
            interests = [row['Interest'] for row in cursor.fetchall()]
            
            cursor.execute('SELECT Goal FROM career_goals WHERE UserID = %s', (userID,))
            career_goals = [row['Goal'] for row in cursor.fetchall()]
            
            cursor.execute('SELECT CareerPath FROM career_path WHERE UserID = %s', (userID,))
            career_paths = [row['CareerPath'] for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM experience WHERE UserID = %s', (userID,))
            experiences = cursor.fetchall()
            
            response_data = {
                'user': user_data,
                'skills': skills,
                'interests': interests,
                'career_goals': career_goals,
                'career_paths': career_paths,
                'experiences': experiences
            }
            
            return jsonify({'message': 'Update successful', 'data': response_data}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error during update: {str(e)}")
            connection.rollback()
            return jsonify({'error': str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

#------------------------------------------------------------
# Update status
@users.route('/user/<userID>/status', methods=['PATCH'])
def update_user_status(userID):
    status = request.json['status']
    query = '''UPDATE users SET Status = %s WHERE UserID = %s'''
    cursor = db.get_db().cursor()
    cursor.execute(query, (status, userID))
    db.get_db().commit()
    return 'User status updated!', 200

#------------------------------------------------------------
# Update reviews
@users.route('/user/<userID>/reviews', methods=['PATCH'])
def update_reviews(userID):
    reviews = request.json['reviews']
    query = '''UPDATE users SET Reviews = %s WHERE UserID = %s'''
    cursor = db.get_db().cursor()
    cursor.execute(query, (reviews, userID))
    db.get_db().commit()
    return 'User reviews updated!', 200

#------------------------------------------------------------
# Remove users
@users.route('/user/<userID>', methods=['DELETE'])
def delete_user(userID):
    query = '''DELETE FROM users WHERE UserID = %s'''
    cursor = db.get_db().cursor()
    cursor.execute(query, (userID,))
    db.get_db().commit()
    return 'User removed!', 200

#------------------------------------------------------------
# Get user based on a specific trait (major, minor, interest, skills, career_goals, career_path)
@users.route('/user/trait', methods=['GET'])
def get_users_by_trait():
    # Validate the trait to prevent SQL injection
    valid_traits = ['Major', 'Minor']
    join_tables = {
        'Interest': 'interests',
        'Skill': 'skills',
        'CareerGoal': 'career_goals',
        'CareerPath': 'career_path'
    }
    
    trait = request.args.get('trait')
    value = request.args.get('value')

    if trait in valid_traits:
        # Query from users table for valid traits
        query = f'''SELECT UserID, fname, lname, joinDate FROM users 
                    WHERE {trait} = %s'''
        cursor = db.get_db().cursor()
        cursor.execute(query, (value,))
    elif trait in join_tables:
        # Query using a join for related tables
        join_table = join_tables[trait]
        query = f'''SELECT u.UserID, u.fname, u.lname, u.joinDate
                    FROM users u
                    JOIN {join_table} jt ON u.UserID = jt.UserID
                    WHERE jt.{trait} = %s'''
        cursor = db.get_db().cursor()
        cursor.execute(query, (value,))
    else:
        # Return error for invalid traits
        return make_response(jsonify({'error': 'Invalid trait specified'}), 400)

    theData = cursor.fetchall()
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response