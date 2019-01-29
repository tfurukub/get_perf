answer_file=""
with open("test.xml","r") as f:
    for line in f:
        answer_file = answer_file + line
print answer_file


