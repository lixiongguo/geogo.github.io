% demo1

fileName='trench.png';
sz=[9,9];

oriImg=imread(fileName);
newImg=waveCollapse(oriImg,4,sz(1),sz(2));
imshow(newImg)

imwrite(newImg,[fileName(1:end-4),'_',num2str(sz(1)),'_',num2str(sz(2)),'.png'])