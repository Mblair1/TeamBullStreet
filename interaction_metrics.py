#get file object 
file1 = open("interactions.txt", "r")
like_counter = 0
dislike_counter = 0
comment_counter = 0

while(True):
    #read next line
    line = file1.readline()
    #check if line is not null 
    if not line: 
        break
    #you can access the line now count the likes
    temp = line.split("[", 1)  
    temp2 = temp[1].split(",", 1)
    num_likes = int(temp2[0])
    like_counter += num_likes

    #counting the dislikes
    temp = line.split(",",3)
    num_dislikes = int(temp[1])
    dislike_counter += num_dislikes

    #counting the comments
    temp2 =temp[2].split("]", 1)
    num_comments = int(temp2[0])
    comment_counter += num_comments

print("Number of likes: %i" %(like_counter))
print("Number of dislikes: %i" %(dislike_counter))
print("Number of comments: %i" %(comment_counter))
#close file
file1.close