# python3-flashcard-builder

# Details

This project is not intended for use as a flashcard manager, but creates flashcard templates on a page.
This is done by creating two pages; one for the prompts and one for the answers. Equal sections are established per the 'interval' - how many questions per slide, which establishes how many elements are there on the x and y directions. These sections are outlined by a line for cutting.

Once the program has been run, it will output all cards to a generated 'sheets' folder. And each subfolder being the index of the set of questions (specified  by the 'interval'). Each contains images for the prompts and answers.

The idea would then be to assemble all of the prompts and answers into a word processor and then print them back-to-back. Thus when cutting them, will get the prompt on the front and the answer on the back. Even if you dont have a back-to-back printing, printer, you can usually just flip the paper over and it will print on the back.

# Usage
* `-s/--source`     A source json file for reading questions off of, see the sample `questions.json` file for the format.
* `-r/--ppi`        An integer specifying the resolution of the A4 page, available in: 72, 96, 150 and 300 PPI.
* `-x/--text-scale` An integer to tell what the scale of the text is, relative to the resolution which determines height/width. The default is 120 but play around to see the results. 
