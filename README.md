# Meme DB
Communication takes images, specifically stupid images from the internet. 

Linking these images into conversation poses two problems

1. Finding them on the internet sometimes requires rolling the dice on accidently flashing "other" images across your screen, something that might be undesirable at work.
2. If the name is in the URL it takes all the fun away from the repient having to open it to understand what you could have just said with words.

## Enter Meme DB!
Meme DB is a horribly written app in Flask for hosting your own repository of images. Users can find the one then want then generate an obfuscated URL to
share with your friends. This allows you to convey those thoughts through stupid internet images and keeps the reader from cheating by reading the URL.

It was originally even more horribly [written in Perl](https://gist.github.com/notroot/731dcc4b82f84f708f4e) but I am now porting it over to 
Python with Flask cause that's what is trendy for me right now.

### Why do I need this?
You don't, you should probably move on.

### How do I deploy this?
Good luck, its kind of undocumented right now, it needs a sqlite databse, which, I don't include the schema for, 
so I should do that. If you know Flask you could probably get it running, maybe, but probably not.

### I have feedback
OK, thanks. You can leave it right over there .....

### Are there any plans to port it to Go?
No, go way. 

