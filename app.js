const fastify = require('fastify')({
    logger: true,
});

fastify.register(require('./routes'));
// Run the server!
fastify.listen(4445, '0.0.0.0', function (err, address) {
    if (err) {
        fastify.log.error(err);
        process.exit(1);
    }
    fastify.log.info(`server listening on ${address}`);
});
