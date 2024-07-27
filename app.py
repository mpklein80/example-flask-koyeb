from flask import Flask
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')

# Define the new table
metadata = MetaData()
new_table = Table('example_table', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('name', String),
                  Column('description', String)
                 )

# Create the table
metadata.create_all(engine)

# Insert a new row
with engine.connect() as connection:
    insert_statement = new_table.insert().values(id=1, name='Sample', description='This is a sample row')
    connection.execute(insert_statement)

app = Flask(__name__)



@app.route('/')
def hello_world():
    return 'Hello Matt from Koyeb'


if __name__ == "__main__":
    app.run()
