""" This is stub of translation texts for sqlite tui """
# coding: utf-8


t_pl = {"sel_db":"Wybierz bazę danych z niżej podanych (jeśli jakieś są) lub wpisz swoją nową nazwę",
        "sel_tb":"Wybierz tabelę z niżej podanych (jeśli jakieś są) lub wpisz swoją nową nazwę",
        "sel_no":"Nazwa jakaś niehalo więc nazwą bedzie _%s.db",
        "mainmenu":["wybierz bazę/tabelę","stwórz bazę","stwórz tabelę", "dodaj pozycje do tabeli", "kasuj pozycje", "pokaż zawartość tabeli", "wykonaj sql", "wyjdź z programu"],
        "sel_st":"najpierw coś wybierz...",
        "db_empty":"Smuteczek...zapomniałeś/zapomniałaś wybrac bazy danych?",
        "db_was_set":"Hmm, juz wybrałeś/aś baze danych, stworzę nową, ale pracuję na starej, póki nie wybierzesz nowej",
        "provide":"Podaj dane wejściowe",
        "has_no_data":"Podana komenda zwróciła pusty wynik",
        "success":"Wykonano pomyślnie  (prawdopodobnie:))",
        "del_extended":"Usuń wiersz o id..\n 0 - pokaż wszystkie wiersze, \n * - by usunąć wszystkie, \n lub 1-5, lub 1,2,4,6-8 \n  - - by wyjsc bez usuwania",
        "notallowed":"Ta operacja nie jest dozwolona, lub niepoprawne dane wejściowe",
        "tbname":"nazwa tabeli",
        "fields":"nazwy pól lub innymi słowy kolumn",
        "separated_by":"rozdzielaj kolejne pozycje ';' średnikiem",
        "select_file_or_input":"Jeśli chcesz rozpocząć nazwę cyfrą - umieść '/' na samym początku nazwy, np /0_costam69",
        "failed":"Niestety operacja nie zakończyła się poprawnie.",
        "will_try_fix":"Program spróbuje skorygować błąd." }

t_en = {"sel_db":"Choose database from below, if any given, or input Your own new name",
        "sel_tb":"Choose table from below, if any given, or input Your own new name",
        "sel_no":"im too lazy and name You provided is kinda not correct, so your db name is _%s.db",
        "sel_st":"select something first",
        "mainmenu":["select db/tb","create db","create tb", "insert to tb", "delete from tb", "show tb", "execute sql", "quit"],
        "db_empty":"Oh noes. You did not select db did you?",
        "db_was_set":"You already selected DB, i'll create new, but work on old one until new selected",
        "provide":"provide Your input",
        "has_no_data":"Selected command has returned empty result set",
        "success":"Command successful. Most probably :)",
        "del_extended":"Del which row, press \n 0 - to see all, \n * - to del all, \n press 1-7 or 1,2,4,6-8 \n - - if mind changed, returns without deletion ",
        "notallowed":"Operation not allowed, or wrong data input",
        "tbname":"table name",
        "separated_by":"separate by ';' semicolon",
        "fields":"fields names in table - collumns",
        "select_file_or_input":"Due to nature of system selection, if You wish to create new item  with digit in front = add '/' before, like /0",
        "failed":"Unfortunately, this operation failed.",
        "will_try_fix":"Program will try to fix error."
        }

t = t_pl
