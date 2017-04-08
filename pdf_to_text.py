from textract import process

with open('out.txt', 'w') as infile:
    text = process('15-214_l6hn.pdf')
    infile.write(text)
    print text