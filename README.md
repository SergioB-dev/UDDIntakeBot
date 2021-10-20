# UDDIntakeBot

<img src="https://user-images.githubusercontent.com/63927113/138163547-521d637e-aba4-48a8-995c-afc2d9997b7e.png" alt="Girl in a jacket" width="200" height="200">
## Current commands

- #### Add mentors `/add_mentor firstName lastName email`:
  - Add mentors to a collective database
  - Alerts intake channel of change
  
- #### Add mentees `/add_mentee firstName lastName email`:
  - Add mentees to a collective database
  - Alerts intake channel of change
  
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
  
  
  
