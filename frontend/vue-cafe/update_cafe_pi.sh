scp -r ./dist/ tpreso01@cafe.zpq.ens-paris-saclay.fr:home/
ssh tpreso01@cafe.zpq.ens-paris-saclay.fr
cd
sudo mv home/dist /var/www
cd /var/www
sudo mv cafe cafe_old
sudo mv dist cafe
