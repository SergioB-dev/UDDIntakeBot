# UDDIntakeBot

<img src="https://user-images.githubusercontent.com/63927113/138163547-521d637e-aba4-48a8-995c-afc2d9997b7e.png" alt="UDD BOT" width="200" height="200">

## Current commands

### Adding members to database

- #### Add mentors `/add_mentor firstName lastName email`:
  - Add mentors to a collective database
  - Alerts intake channel of change
  
- #### Add mentees `/add_mentee firstName lastName email`:
  - Add mentees to a collective database
  - Alerts intake channel of change

### Getting information
  
- #### Get Latest `/get latest preferredFormat`:
  - Slack bot will DM you with a file of the latest Mentor/Mentee database
    - Supported file formats right now:
    
      - [x] csv
      - [ ] pdf
      - [ ] xlsv
      
- #### Search `/find firstOrLastName`:
  - Returns the result for mentioned member:
    - role (mentor or mentee)
    - first name
    - last name
    - email

- #### Stats `/stats`:
  - Returns big picture stats
    - Mentee to Mentor ratio
    - How many mentees are not paired (near future)
    - More to come! ⏱
      
### Leaving feedback      

- #### Leave feedback `/suggestion yourFeedback`:
  - Leave feedback for improvements, this is v1 after all!
  
  
## Future commands

- #### Get details `/get_details nameOrEmail`:
  - Returns you details of member:
    - role ( mentee or mentor )
    - first name
    - last name
    - email
    - isPaired (True if paired, False if not), also returns paired partner
    - join date
    - briefing (details gathered from when they joined)
    - tech stack

- #### Find all potential matches `/match mentee`:
  - Searches database for mentioned mentee and finds potential matches based on tech stack

- #### Bulk insert `/add_doc`:
  - Take a doc (csv for example) and parse every line and add every mentor/mentee from the doc
  
  
  
