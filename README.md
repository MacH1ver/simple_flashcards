## simple_flashcards
Simple flashcards is a python script that takes an xlsx file with questions and answers and creates flashcards from that. The idea is to use an LLM like ChatGPT to make the questions and answers.

This is still a work in progress so some day down the line it will probably get more sophisticated.

### How to use:
1. Ask your favorite LLM to make you an .xlsx file with two columns, one for questions and one for answers and to fill those in with the relevant questions for your project. 
2. Save the file in a easy to access place and copy the file path.
3. Open the file in your favorite IDE. Replace the file name on line 7 in the code with the path to where you have stored you file with questions and answers. 
4. Run the script. 

### Required packages:

As of now the required packages are:
- pandas
- tkinter
- random
