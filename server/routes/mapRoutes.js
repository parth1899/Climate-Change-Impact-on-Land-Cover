const express = require('express');
const router = express.Router();
const { generateMaps } = require('../controllers/mapController');

router.post('/generate', generateMaps);

module.exports = router;