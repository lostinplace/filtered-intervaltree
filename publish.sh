export LIBVER=$1
python setup.py egg_info
python setup.py bdist_wheel
twine register dist/filtered_intervaltree-$LIBVER-py3-none-any.whl
twine upload dist/filtered_intervaltree-$LIBVER-py3-none-any.whl
echo $LIBVER > .library-version