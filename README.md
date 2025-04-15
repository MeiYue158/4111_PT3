# 4111 Project 1 - Part 3 Web Application

## Group Information
- Group Number: 16
- Members: Mei Yue,     
           (Another teammate was completely unresponsive throughout the entirety of Project 3, and only informed me on the final day before the deadline that she was dropping the course.)

## Database Account
- PostgreSQL Username: my2903
- Database Name: proj1part2

## Web Application URL
- You can access the live demo of my web application here:

    [http://34.138.112.142:8111](http://34.138.112.142:8111)

- **Note:** Achieved this step: Flask server is hosted using `screen` to ensure persistence.

## Description of Implemented Features

### Implemented Pages
1. **User Registration Page** (`/create_user`)  
   - Allows user to register with personal information.
   - Supports dropdowns for country/city, occupation, income.
   - Validates emails and prevents duplicates.


   #### Detailed Design:
   - **Country & City Selection (Two-Level Dropdown)**  
     Users begin registration by selecting their country. Currently, we support **China** and **USA**. Once a country is selected, the **City** dropdown dynamically updates to show only valid city options relevant to that country. This two-level cascading dropdown design ensures accuracy and simplifies the user input process.

   - **Email Format Validation**  
     The email field includes built-in validation using a regular expression (`email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'`).  
     If a user enters an incorrectly formatted email (e.g., missing "@"), the system will show an error:  
     **"Invalid email format. Please go back and enter a valid email."**  
     This prevents faulty or unusable records from being stored in the database.

   - **First Name & Last Name**  
     These fields are simple text inputs where users can freely enter their names. They are required for uniquely identifying and personalizing users throughout the trip planning process.

   - **Date of Birth (DOB) Constraint**  
     The date picker for DOB ensures users **cannot select a future date**. For example, if today is April 7, 2025, users can only pick April 7 or earlier.

   - **Gender Selection**  
     Users can select gender from:
     - male  
     - female  
     - non-binary  
     - other  
     - prefer not to say  

   - **Preferred Travel Type**  
     This is a **free text input** where users can describe their travel preferences in their own words (e.g., "solo backpacking", "family-oriented").

   - **Occupation Options**  
     The **Occupation** dropdown includes:
     - student  
     - teacher  
     - engineer  
     - artist  
     - unemployed  
     - retired  
     - other  

   - **Income Bracket Selection**  
     The **Income** dropdown categorizes user income:
     - up to $50K  
     - $50–100K  
     - $100–200K  
     - more than $200K  
     - prefer not to say  


2. **Trip Creation Page** (`/create_trip`)  
   - Users specify travel dates, number of adults/children.
   - Automatically links trip to user and inserts into database.

   #### Detailed Design:
   - **Trip Group Composition**  
     Users can specify the number of adults and children they are traveling with. Both fields are numeric inputs constrained to accept values **greater than or equal to 0**, ensuring valid and realistic input about the group composition.

   - **Trip Date Range Selection with Validation**  
     The page allows users to select a **Begin Date** and an **End Date** for their trip.  
     The system includes built-in validation to ensure that the **begin date is not later than the end date**.  
     If an invalid range is entered (e.g., start date after end date), the system displays an alert message prompting the user to correct the input.


3. **Trip Details Page** (`/trip_details`)  
   - Allows input of hotel, restaurant, experience, and transportation data.
   - Supports multiple entries for each type.
   - Final submission inserts everything and clears session.

   #### Detailed Design:
   - **Hotel Accommodation**  
     Users can select from real Disneyland hotel names.  
     Hotel type and room type are selectable from dropdowns.  
     Nights stayed accepts only non-negative integers.  
     Hotel cost must be a non-negative float with up to 2 decimal places.

   - **Dining Experience**  
     Users input the restaurant name and select which Disneyland park it is located in.  
     Meal type and meal time are both selectable to describe the dining experience.  
     Meal cost input must be a non-negative float.

   - **Visited Parks**  
     Supports selection of **multiple** parks (checkboxes), such as Magic Kingdom, EPCOT, etc.

   - **Experiences**  
     Allows input of additional activities like photo ops or makeovers.  
     Includes name, category, park, payment method, purchase time, and cost (non-negative float).

   - **Ticket Cost**  
     Captures ticket purchase cost and time.

   - **Transportation**  
     Allows input of total transportation cost related to the trip.


#### Key Workflow Behaviors
- User must complete all required registration fields before proceeding to the Trip Creation Page.
- Users must fill in all required trip info before accessing the Trip Details Page.
- Trip Details Page includes a **Back** button that retains all data entered in the previous step (thanks to session caching).
- **Save** button on the Trip Details Page temporarily stores data for later completion.
- **Submit** button is only enabled if all fields are valid and completed; otherwise, the system displays which field(s) are missing.
- Upon successful submission, the user sees a confirmation screen and is redirected back to the registration page.


## How to Run
1. Clone repo: `git clone https://github.com/MeiYue158/4111_PT3.git`
2. SSH into VM and run:
```bash
cd 4111_PT3
python3 server.py
