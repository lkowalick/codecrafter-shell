FROM python:3

WORKDIR /usr/src/app

RUN pip install pipenv
RUN pipenv install
COPY . .

CMD [ "./your_program.sh" ]
