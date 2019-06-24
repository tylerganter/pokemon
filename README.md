This project investigates the pokemon game series to find
the most powerful pokemon.

It is an end-to-end process starting with data acquisition from various
websites and ending with a final web application GUI for requesting and
visualizing results.


## Local MySQL Configuration:

These instructions are for macOS. It shouldn't be much of a stretch to make it
work on linux. If you're on windows...well, I pity you.

I installed mysql using [homebrew](https://brew.sh/).

```
brew services start mysql
brew services stop mysql
```

Well, start it up, and then lets make our database and database user:

```
mysql -u root -p
```

```
create database <DATABASE>;
create user '<USERNAME>'@'localhost' identified by '<PASSWORD>';
grant all privileges on <DATABASE>.* to '<USERNAME>'@'localhost';
exit
```
Put the following at the bottom of your `~/.bash_profile` file:

```
export CLOUD_SQL_USERNAME="<USERNAME>"
export CLOUD_SQL_PASSWORD="<PASSWORD>"
export CLOUD_SQL_DATABASE_NAME="<DATABASE>"
mysqlpoke() { mysql -u $CLOUD_SQL_USERNAME -p$CLOUD_SQL_PASSWORD $CLOUD_SQL_DATABASE_NAME; }
```

and run `source ~/.bash_profile`. You can now call `mysqlpoke` from the command line to be logged into mysql as the newly created user.

## Virtual Environment

Now install [virtualenv](https://virtualenv.pypa.io) for python, and add this to your `~/.bash_profile` file:

```
export ENV_DIR="/<PATH>/<TO>/<YOUR>/<ENVIRONMENTS>"
poke() { source "${ENV_DIR}/poke/bin/activate"; }
exit() {
    case `command -v python` in
        ${ENV_DIR}/*) deactivate;;
        *) builtin exit;;
    esac
}
```

`/<PATH>/<TO>/<YOUR>/<ENVIRONMENTS>` can be any arbitrary directory, such as `/Users/<username>/envs/`.

Now we can create the virtual environment:
```
virtualenv $ENV_DIR/pokemon
```

We can activate it at any point by `poke`, deactivate it with `exit`, and if we ever need to reset the environment, just make it fresh:

```
rm -rf $ENV_DIR/pokemon
virtualenv $ENV_DIR/pokemon
```
