import sqlite3

connection = None
cursor = None


def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return


def drop_tables():
    global connection, cursor

    drop_users = "DROP TABLE IF EXISTS users; "
    drop_follows = "DROP TABLE IF EXISTS follows; "
    drop_tweets = "DROP TABLE IF EXISTS tweets; "
    drop_hashtags = "DROP TABLE IF EXISTS hashtags"
    drop_mentions = "DROP TABLE IF EXISTS mentions"
    drop_retweets = "DROP TABLE IF EXISTS retweets"
    drop_lists = "DROP TABLE IF EXISTS lists"
    drop_includes = "DROP TABLE IF EXISTS includes"


    cursor.execute(drop_follows)
    cursor.execute(drop_mentions)
    cursor.execute(drop_hashtags)
    cursor.execute(drop_retweets)
    cursor.execute(drop_includes)
    cursor.execute(drop_lists)
    cursor.execute(drop_tweets)
    cursor.execute(drop_users)


def define_tables():
    global connection, cursor

    users_query = '''
        create table users
            (
                usr      varchar(10)
                    primary key,
                name     text,
                email    text,
                city     text,
                timezone float,
                pwd      text
            );
    '''

    follows_query = '''
        create table follows
            (
                flwer      int
                    references users,
                flwee      int
                    references users,
                start_date date,
                primary key (flwer, flwee)
            );
    '''

    tweets_query = '''
        create table tweets
            (
                tid       int,
                writer    int references users,
                tdate     date,
                text      text,
                replyto   int,
                primary key (tid),
                foreign key (writer) references users (usr),
                foreign key (tid) references tweets (tid)
            );
    '''

    hashtags_query = '''
        create table hashtags
            (
                term text
                    primary key
            );
    '''

    mentions_query = '''
        create table mentions
            (
                tid int,
                term   text references hashtags,
                primary key (tid, term),
                foreign key (tid) references tweets
            );
    '''

    retweets_query = '''
        create table retweets
            (
                usr    int references users,
                tid int,
                rdate  date,
                primary key (usr, tid),
                foreign key (tid) references tweets,
                foreign key (usr) references users
            );
    '''

    lists_query = '''
        create table lists
            (
                lname text
                    primary key,
                owner int
                    references users
            );
    '''

    includes_query = '''
        create table includes
            (
                lname  text
                    references lists,
                member int
                    references users,
                primary key (lname, member)
            );
    '''

    cursor.execute(users_query)
    cursor.execute(follows_query)
    cursor.execute(tweets_query)
    cursor.execute(hashtags_query)
    cursor.execute(mentions_query)
    cursor.execute(retweets_query)
    cursor.execute(lists_query)
    cursor.execute(includes_query)

    connection.commit()

    return


def insert_data():
    global connection, cursor

    insert_users = '''
        insert into main.users (usr, name, email, city, timezone, pwd)
        values  ('matthew', 'Matthew', 'matthew@example.com', 'Calgary', -6, '12345'),
            ('matthew2', 'Another Matthew', 'matthew1@example.com', 'Edmonton', -6, '54321'),
            ('joshua', 'Joshua', 'joshua@example.com', 'Edmonton', -6, 'supersafepassword'),
            ('joshua2', 'Another Joshua', 'joshua1@example.com', 'Edmonton', -7, 'extrasafepassword'),
            ('rj', 'RJ', 'rj@example.com', 'Edmonton', -2, 't00S@fe'),
            ('kelvin', 'Kelvin', 'kelvin@example.com', 'Edmonton', -1, 'badpassword');
    '''

    insert_tweets = '''
        insert into main.tweets (tid, writer, tdate, text, replyto)
        values  
            (0, 'matthew', '2023-05-01', 'Hello World', null),
            (1, 'matthew', '2023-05-02', 'Hello', 0),
            (2, 'joshua2', '2023-05-03', 'How is it going today', 0),
            (3, 'rj', '2023-05-04', 'Its a new month!', null),
            (4, 'matthew2', '2023-05-29', 'What just happened?', null),
            (5, 'kelvin', '2023-05-30', 'Something just exploded!', 4),
            (6, 'joshua', '2023-05-31', 'I saw it too!', 5),
            (7, 'joshua2', '2023-05-31', 'Wow', 5),
            (8, 'matthew', '2023-06-1', 'RIGHT!!!', 7);
    '''

    insert_hashtags = '''
        insert into main.hashtags (term)
            values
                ('hello'),
                ('crazy');
    '''

    insert_mentions = '''
        insert into main.mentions (tid, term)
            values
                (0, 'hello'),
                (1, 'hello'),
                (4, 'hello'),
                (4, 'crazy'),
                (7, 'crazy'),
                (8, 'crazy');
    '''

    insert_lists = '''
        insert into main.lists (lname, owner)
            values  ('oilers players', 'matthew2'),
                ('pc', 'matthew2'),
                ('liberal', 'kelvin'),
                ('ndp', 'joshua2'),
                ('book lovers', 'joshua2'),
                ('art lovers', 'joshua'),
                ('science nerds', 'kelvin'),
                ('movie night crew', 'rj'),
                ('beach lovers', 'kelvin'),
                ('gourmet chefs', 'matthew'),
                ('science fiction fans', 'rj');
    '''

    insert_includes = '''
        insert into main.includes (lname, member)
            values  ('science nerds', 'rj'),
                    ('science fiction fans', 'matthew');
    '''

    insert_followers = '''
        insert into main.follows (flwer, flwee, start_date)
            values  ('matthew2', 'rj', '2022-04-01'),
                    ('matthew2', 'kelvin', '2022-04-02'),
                    ('matthew2','matthew', '2022-06-28'),
                    ('rj', 'matthew2', '2023-05-15'),
                    ('kelvin', 'rj', '2023-06-19'),
                    ('rj', 'kelvin', '2023-07-20'),
                    ('matthew','matthew2','2023-11-05');
    '''

    insert_retweets = '''
        insert into main.retweets (usr, tid, rdate)
            values ('rj', 3, '2023-05-05'),
                   ('kelvin', 4, '2023-05-05'),
                   ('joshua2', 5, '2023-05-12'),
                   ('joshua', 3, '2023-05-23');
    '''

    cursor.execute(insert_users)
    cursor.execute(insert_tweets)
    cursor.execute(insert_hashtags)
    cursor.execute(insert_mentions)
    cursor.execute(insert_lists)
    cursor.execute(insert_includes)
    cursor.execute(insert_followers)
    cursor.execute(insert_retweets)



    connection.commit()
    return


def main():
    global connection, cursor

    path = "./db1.db"
    connect(path)
    drop_tables()
    define_tables()
    insert_data()

    connection.commit()
    connection.close()
    return


if __name__ == "__main__":
    main()