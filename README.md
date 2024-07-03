# для запуска нужно следующее
```
wget -nc https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -f ./google-chrome-stable_current_amd64.deb
git clone https://github.com/DenisKadyrov/vk_market_parser.git
cd vk_market_parser
pip install -r requirements.txt
python parser.py
```
