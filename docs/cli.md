# Command Line Reference

## Getting help

You can allways use `shellcraft --help` to see all available commands, or `shellcraft <command> --help` to get help on a particular command.

Additionally, `shellcraft tutorial` will display the last tutorial message.

## Mining

Use `shellcraft mine <resource>` to mine a resource.

## Crafting items

See a list of available items to craft with `shellcraft craft`, and craft an item with `shellcraft craft <item>`. The resources required will be immediately consumed.

## Research

Like crafting items, `shellcraft research` lists available project, and `shellcraft research <project>` starts research on a particular one.

## Seeing your inventory

You can see all available resources with `shellcraft resources`, or only how much of a particular resource you have with `shellcraft resources <resource>`.

Use `shellcraft inventory` to see items in your posession.

# Automating the game

"Hacking" the game with command line scripts is not only possible, but encouraged. Many people include an `alias sc=shellcraft` into their `.bashrc` or `.bash_profile`.

You can write scripts like this one to e.g. automatically mine 10 ore with `./mine.sh ore 10`:

```sh
#!/usr/bin/env sh
for i in `seq 1 $2`; do
    shellcraft mine $1
done
```
