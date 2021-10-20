const fs = require('fs');
const path = require('path');
const {MediaController} = require('../controllers');

async function routes(fastify, options) {
    fastify.get('/puzzles/:name', async (request, reply) => {
        try {
            const name = request.params.name;
            const count = request.params.count;
            if (!name) {
                return reply.send({err: 'ERROR'});
            }
            const puzzles = await MediaController.GetRandomPuzzles(name, count);
            console.log('puzzles', puzzles);
            return reply.send({names: puzzles});
        } catch (err) {
            console.log('err', err);
            reply.send({err: 'ERROR'});
        }
    });
    fastify.get('/puzzle/:name', async (request, reply) => {
        try {
            const name = request.params.name;
            if (!name) {
                return reply.send({err: 'ERROR'});
            }
            const img = fs.readFileSync(
                path.join(__dirname, '../media', name.split('.')[0], name)
            );
            reply.send(img);
        } catch (err) {
            console.log('err', err);
            reply.send({err: 'ERROR'});
        }
    });
    fastify.get('/puzzle/:name/holed', async (request, reply) => {
        try {
            const name = request.params.name;
            if (!name) {
                return reply.send({err: 'ERROR'});
            }
            const img = fs.readFileSync(
                path.join(
                    __dirname,
                    '../media',
                    name.split('.')[0],
                    name.split('.')[0] + '_holed.' + name.split('.')[1]
                )
            );
            reply.send(img);
        } catch (err) {
            console.log('err', err);
            reply.send({err: 'ERROR'});
        }
    });
    fastify.get('/puzzle/:name/peace/:peace', async (request, reply) => {
        try {
            // console.log('request.params.name', request.params.peace);
            if (!request.params.name || !request.params.peace) {
                return reply.send({err: 'ERROR'});
            }
            const img = fs.readFileSync(
                path.join(
                    __dirname,
                    '../media',
                    request.params.name.split('.')[0],
                    request.params.peace
                )
            );
            reply.send(img);
        } catch (err) {
            console.log('err', err);
            reply.send({err: 'ERROR'});
        }
    });
    fastify.get('/puzzle/:name/metadata.json', async (request, reply) => {
        console.log('request. metadata', request.params.name);

        try {
            if (!request.params.name) {
                return reply.send({err: 'ERROR'});
            }
            await MediaController.onMakePuzzle({
                name: request.params.name,
                url: request.params.name,
            });
            const img = fs.readFileSync(
                path.join(
                    __dirname,
                    '../media',
                    request.params.name,
                    'metadata.json'
                )
            );

            reply.send(img);
        } catch (err) {
            console.log('err', err);
            reply.send({err: 'ERROR'});
        }
    });
}

module.exports = routes;
