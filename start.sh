pwd

source /home/mmt/anaconda3/etc/profile.d/conda.sh

conda activate .venv_py311

pip install -r ./requirements.txt

python main.py --crawl_aigc 1