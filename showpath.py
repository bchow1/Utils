#!/c/Users/sid/Anaconda2/python
echo $PATH | python -c "import sys; lines = [ line.replace(':','\n') for line in sys.stdin ]; lines.sort();print lines[0]"
