This project investigates the pokemon game series to find
the most powerful pokemon.

It is an end-to-end process starting with data acquisition from various
websites and ending with a final web application GUI for requesting and
visualizing results.


# Local MySQL Configuration:

These instructions are for macOS. It shouldn't be much of a stretch to make it
work on linux. If you're on windows...well, I pity you.

I installed mysql using [homebrew](https://brew.sh/).

```
mysql -u root -p
```

```
create database <DATABASE>;
create user '<USERNAME>'@'localhost' identified by '<PASSWORD>';
grant all privileges on <DATABASE>.* to '<USERNAME>'@'localhost';
exit
```

mysql -u $CLOUD_SQL_USERNAME -p$CLOUD_SQL_PASSWORD $CLOUD_SQL_DATABASE_NAME

```
export CLOUD_SQL_USERNAME="<USERNAME>"
export CLOUD_SQL_PASSWORD="<PASSWORD>"
export CLOUD_SQL_DATABASE_NAME="<DATABASE>"
mysqlpoke() { mysql -u $CLOUD_SQL_USERNAME -p$CLOUD_SQL_PASSWORD $CLOUD_SQL_DATABASE_NAME; }
```