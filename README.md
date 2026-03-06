## simple_flashcards
Simple flashcards is a python script that takes an .xlsx or .csv file with questions and answers and creates flashcards from that. The idea is to use an LLM like ChatGPT to make the questions and answers.

### How to use:
1. Ask your favorite LLM to make you an .xlsx or .csv file with two columns, one for questions and one for answers and to fill those in with the relevant questions for your project. 
2. Run the script
3. Click the hamburger menu in the top right and click on drag and drop
4. Drag your file to the window
5. Choose if you want the questions in sequential or random order
6. Learn!
7. In the same folder as the script a session.json file will be saved. That's where the previous question files will be so after you close it down you can go back and use the same file without having to drag it in again.
8. Navigation can be done with the arrow keys, left arrow for next, right arrow for previous and up or down arrow to reveal the answer.

### Required packages:

As of now the required packages are:
- [pandas](https://pandas.pydata.org/)
- [tkinter](https://docs.python.org/3/library/tkinter.html)
- [random](https://docs.python.org/3/library/random.html#module-random)
- [json](https://www.json.org/json-en.html)
- [pathlib](https://docs.python.org/3/library/pathlib.html)
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/)
