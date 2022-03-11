"""

@app.route('/add_mentor', methods=['POST'])
def add_mentor():
    #user_input
    # [0] == first name
    # [1] == last name
    # [2] == email
    data = request.form
    user_input = data.get('text').split(' ')
    # TODO: Add safety checks that all input is received before accessing them on next line

    add_member_to_db(user_input[1].capitalize(), user_input[0].capitalize(), user_input[2], 'Mentor')
    post_message(f'{user_input[0]} has been added to the database as a mentor. ✅')
    return Response(), 200

    @app.route('/post', methods=['POST'])
def test_external_post():
    print('this is working')
    post_message('Bot coming back online...', '#intake')
    return Response(), 200

@app.route('/stats', methods=['POST'])
def stats():
    data = request.form
    user_id = data.get('user_id')

    both_counts = db_stats()
    mentee_count = both_counts[0]
    mentor_count = both_counts[1]
    ratio = ratios(mentee_count, mentor_count)
    post_message(ratio, channel=user_id)

    return Response(), 200


@app.route('/add_mentee', methods=['POST'])
def add_member():
    # user_input
    # [0] == first name
    # [1] == last name
    # [2] == email
    data = request.form
    user_input = data.get('text').split(' ')
    # TODO: Add safety checks that all input is received before accessing them on next line

    add_member_to_db(user_input[1].capitalize(), user_input[0].capitalize(), user_input[2], 'Mentee')
    post_message(f'{user_input[0]} has been added to the database as a mentee. ✅')
    print(user_input)
    return Response(), 200

    # Method for uploading csv/pdf/etc. files
@app.route('/get', methods=['POST'])
def get_data():

    data = request.form
    user_input = data.get('text').split(' ')
    user_id = data.get('user_id')               # ID of user who made the request
    # TODO: Add safety checks that all input is received before accessing them on next line
    print(data)
    if user_input[1] == 'csv':              # user_input[1] here should be some data format specified by the user
        convert_db_to_csv()                 # Check and see whether we should update latest working version
        upload_file('output/output.csv', channel=user_id)      # Passing the user id as the channel is essentially a DM
        post_message(FEEDBACK_PROMPT, user_id)           # Asking user for feedback in DM

    else:
        pass

    return Response(), 200

    def upload_file(file, channel='C02HYQDP7EZ'):
    try:
        result = client.files_upload(
            channels=channel,
            initial_comments='Testing',
            file=file
        )
        logger.info(result)

    except SlackApiError as e:
        logger.error(f'Error uploading file: {e}')

"""