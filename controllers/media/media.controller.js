const spawn = require('child_process').spawn;
const path = require('path');
const axios = require('axios');
const fs = require('fs');
const items = require('./items.json');
const scriptFilename = path.join(__dirname, '../../Peacer/app.py');

const onMakePuzzle = async ({name, url}) => {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', [scriptFilename, name]);
        pythonProcess.stdout.on('data', (data) => {
            const response = data.toString();
            if (
                response &&
                response.length &&
                response.substr(0, 4) === 'True'
            ) {
                resolve();
            } else {
                reject('err');
            }
        });
    });
};

const GetRandomPuzzles = (name, count = 3) => {
    return new Promise((resolve, reject) => {
        const p = path.resolve(__dirname, '../../media', name);
        fs.readdir(p, async (err, files) => {
            if (err) throw err;
            if (!files.length) {
                resolve([]);
            } else {
                const parsedFiles = await getExistingFiles(
                    files.map((f) => f + '.png')
                );
                if (parsedFiles.length < count) {
                    return resolve(parsedFiles.map((f) => f.split('.')[0]));
                }
                let list = [];
                let i = 0;
                while (i < count) {
                    const ind = parseInt(Math.random() * parsedFiles.length);
                    const name = parsedFiles[ind].split('.')[0];
                    if (list.indexOf(name) < 0) {
                        list.push(name);
                        i++;
                    }
                }
                resolve(list);
            }
        });
    });
};

module.exports = {
    onMakePuzzle,
    GetRandomPuzzles,
};
const getMoonshotBotsMetadata = () => {
    return Promise.all(
        items.map((item, i) =>
            getCollectionMetadata(
                // 'https://ipfs.io//api/v0/ls?arg=QmTW4BpWieHw5nwNC6xcyVQfdmU5nZU4M3Lm2ZpFVXZCGi'
                // 'https://ipfs.io/ipfs/QmdRmZ1UPSALNVuXY2mYPb3T5exn9in1AL3tsema4rY2QF/json/'
                // 'https://gateway.pinata.cloud/ipfs/QmdRmZ1UPSALNVuXY2mYPb3T5exn9in1AL3tsema4rY2QF/json/',
                'https://gateway.pinata.cloud/ipfs/QmShqhZzwkoEM1wcrWjG7HTvPUgvBaknRqaFhBUNMvis1T/nfts/',
                item,
                i
            )
        )
    );
};
const getCollectionMetadata = (url, name, i) => {
    return new Promise((resolve, reject) => {
        setTimeout(async () => {
            const dir = path.resolve(
                __dirname,
                '../../media',
                'moonshotbotsv3',
                name.split('.')[0]
            );
            console.log('dir', dir);
            const p = path.resolve(dir, name);
            !fs.existsSync(dir) && fs.mkdirSync(dir);
            console.log(i);
            const writer = fs.createWriteStream(p);

            axios({
                url: url + name,
                method: 'GET',
                responseType: 'stream',
            })
                .then((response) => {
                    response.data.pipe(writer);
                    writer.on('finish', resolve);
                    writer.on('error', (err) => {
                        console.log('err', err);
                        resolve();
                    });
                })
                .catch((err) => {
                    console.log('err', err);
                    resolve();
                });
        }, 750 * i);
    });
};

const getExistingFiles = (cItems) => {
    return new Promise((resolve, reject) => {
        const pItems = cItems || items;
        let de = 0;
        let e = [];
        for (let i = 0; i < pItems.length; i++) {
            const name = pItems[i];
            const dir = path.resolve(
                __dirname,
                '../../media',
                'moonshotbotsv3',
                name.split('.')[0]
            );
            const p = path.resolve(dir, name);
            if (fs.existsSync(p) && fs.statSync(p).size > 0) {
                e.push(name);
            } else {
                de++;
            }
        }
        console.log('exists', e);
        console.log('doesnt exists', de);
        resolve(e);
    });
};

// getMoonshotBotsMetadata();
