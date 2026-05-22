% demo2

fileName='celtic3e.png';
sz=[15,15];

oriImg=imread(fileName);
newImg=waveCollapse(oriImg,9,sz(1),sz(2));
imshow(newImg)

imwrite(newImg,[fileName(1:end-4),'_',num2str(sz(1)),'_',num2str(sz(2)),'.png'])