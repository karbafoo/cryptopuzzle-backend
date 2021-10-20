async function routes(fastify, options) {
    fastify.register(require('./media'), {prefix: '/media'});
    fastify.get('/', async (request, reply) => {
        return {hello: 'world'};
    });
}

module.exports = routes;
