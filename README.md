# Defi Stats Backend

Dies ist das Backend Repo für [Defi Stats](https://github.com/chnuessli/defi_stats)

## Python App mit Flask

Das Backend wurde in Flask geschrieben und wird ASAP hier nachdokumentiert.

## convert github token to git encoded data
at first you have to convert github token to encoded data. If you use original github token, You can't use on Azure or any other platform.

So we need encoded github token data.

```bash

python convert.py github_pat_XXXX
```
You can get encoded git_data : XXXXXX

## put encoded data to defiback/__init__.py line 13 

like this

```bash
git_data = "Z2l0aHViX3BhdF8xMUFQQ1M3QVkwUXlWZXNBcGV5MWtMX3RnQW81Vm04azd5b0lyRlF3OTlGeVZmVEFFQmFFb3pzN2JWRkZva0xkTVJMUVlEN1o3Q2lEa3h6OHJp"

```