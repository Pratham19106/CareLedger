const express = require('express');

const { authenticate } = require('../middlewares/authMiddleware');
const { requireRole, requireVerifiedDoctor } = require('../middlewares/roleMiddleware');
const doctorController = require('../controllers/doctorController');

const router = express.Router();


router.use(authenticate);

router.get('/', requireRole('doctor'), doctorController.getOwnProfile);
router.post('/', requireRole('doctor'), doctorController.createDoctorProfile);
router.put('/', requireRole('doctor'), doctorController.updateOwnProfile);
router.get('/consultations', requireVerifiedDoctor, doctorController.getOwnConsultations);
router.get('/:id', doctorController.getDoctorById);

module.exports = router;
