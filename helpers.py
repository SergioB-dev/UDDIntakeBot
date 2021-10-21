# Returns ratio of 2 numbers in str format
# Ex: '2:1'

def ratios(num1, num2):
    mentee_count = num1
    mentor_count = num2

    if mentee_count > mentor_count:
        ratio = mentee_count / mentor_count
        return '{:.1f} : 1.0 Ratio of Mentees to Mentors ð'.format(ratio)
    elif mentor_count > mentee_count:
        ratio = mentor_count / mentee_count
        return '{:.1f} : 1.0 Ratio of Mentors to Mentees ð'.format(ratio)
    else:
        return 'Even ratio of 1:1 of Mentors to Mentees ð'


