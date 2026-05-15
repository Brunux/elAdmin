from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        self._create_users()
        towers = self._create_towers()
        apartments = self._create_apartments(towers)
        residents = self._create_residents(apartments)
        self._create_payments(apartments, residents)
        self._create_announcements()
        self._create_issues(apartments, residents)

        self.stdout.write(self.style.SUCCESS('Done.'))

    # ------------------------------------------------------------------
    def _create_users(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@eladmin.local', 'admin123',
                                          first_name='Admin', last_name='Sistema')
            self.stdout.write('  created superuser admin')

        staff_data = [
            ('staff', 'staff@eladmin.local', 'staff123', 'Carlos', 'Méndez'),
            ('staff2', 'staff2@eladmin.local', 'staff123', 'Laura', 'Castillo'),
        ]
        for username, email, password, first, last in staff_data:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username, email, password,
                                         first_name=first, last_name=last,
                                         is_staff=True)
                self.stdout.write(f'  created staff {username}')

    def _create_towers(self):
        from apps.towers.models import Tower
        towers_data = [
            ('Orión',  1, 12, 'Torre principal con vista al parque'),
            ('Sirio',  2, 10, 'Torre sur con piscina en azotea'),
            ('Altair', 3,  8, 'Torre norte, acceso directo al jardín'),
        ]
        towers = []
        for name, number, floors, desc in towers_data:
            t, created = Tower.objects.get_or_create(
                number=number,
                defaults=dict(name=name, floors=floors, description=desc),
            )
            towers.append(t)
            if created:
                self.stdout.write(f'  created tower {t}')
        return towers

    def _create_apartments(self, towers):
        from apps.units.models import Apartment
        # (tower_idx, number, floor, status, area, fee)
        apts_data = [
            # Torre Orión — 14 apartments
            (0, '101', 1, 'occupied',    72.5, 1800),
            (0, '102', 1, 'vacant',      70.0, 1800),
            (0, '103', 1, 'occupied',    70.0, 1800),
            (0, '104', 1, 'occupied',    72.5, 1800),
            (0, '201', 2, 'occupied',    85.0, 2100),
            (0, '202', 2, 'occupied',    85.0, 2100),
            (0, '203', 2, 'vacant',      80.0, 2000),
            (0, '204', 2, 'occupied',    85.0, 2100),
            (0, '301', 3, 'maintenance', 90.0, 2200),
            (0, '302', 3, 'occupied',    90.0, 2200),
            (0, '303', 3, 'occupied',    88.0, 2150),
            (0, '401', 4, 'occupied',   100.0, 2500),
            (0, '402', 4, 'occupied',   100.0, 2500),
            (0, '403', 4, 'vacant',      98.0, 2450),
            # Torre Sirio — 12 apartments
            (1, '101', 1, 'occupied',    68.0, 1750),
            (1, '102', 1, 'occupied',    68.0, 1750),
            (1, '103', 1, 'vacant',      66.0, 1700),
            (1, '201', 2, 'occupied',    80.0, 2000),
            (1, '202', 2, 'occupied',    80.0, 2000),
            (1, '203', 2, 'occupied',    78.0, 1950),
            (1, '301', 3, 'occupied',    95.0, 2400),
            (1, '302', 3, 'occupied',    95.0, 2400),
            (1, '303', 3, 'occupied',    92.0, 2300),
            (1, '401', 4, 'vacant',     105.0, 2600),
            (1, '402', 4, 'occupied',   105.0, 2600),
            (1, '403', 4, 'occupied',   102.0, 2550),
            # Torre Altair — 9 apartments
            (2, '101', 1, 'occupied',    65.0, 1650),
            (2, '102', 1, 'occupied',    65.0, 1650),
            (2, '103', 1, 'vacant',      63.0, 1600),
            (2, '201', 2, 'occupied',    75.0, 1900),
            (2, '202', 2, 'occupied',    75.0, 1900),
            (2, '203', 2, 'occupied',    73.0, 1850),
            (2, '301', 3, 'occupied',    88.0, 2200),
            (2, '302', 3, 'occupied',    88.0, 2200),
            (2, '303', 3, 'vacant',      85.0, 2100),
        ]
        apartments = []
        for t_idx, number, floor, status, area, fee in apts_data:
            apt, created = Apartment.objects.get_or_create(
                tower=towers[t_idx],
                number=number,
                defaults=dict(floor=floor, status=status, area_sqm=area, monthly_fee=fee),
            )
            apartments.append(apt)
            if created:
                self.stdout.write(f'  created apartment {apt}')
        return apartments

    def _create_residents(self, apartments):
        from apps.residents.models import Resident

        residents_data = [
            ('juan@example.com',      'pass1234', 'Juan',      'García',     '555-0101', 'owner',  0,  date(2022, 3,  1)),
            ('maria@example.com',     'pass1234', 'María',     'López',      '555-0102', 'tenant', 2,  date(2023, 6, 15)),
            ('pedro@example.com',     'pass1234', 'Pedro',     'Ruiz',       '555-0103', 'owner',  3,  date(2021, 1, 10)),
            ('ana@example.com',       'pass1234', 'Ana',       'Torres',     '555-0104', 'tenant', 4,  date(2024, 2,  1)),
            ('luis@example.com',      'pass1234', 'Luis',      'Vargas',     '555-0105', 'owner',  5,  date(2020, 8, 20)),
            ('sofia@example.com',     'pass1234', 'Sofía',     'Herrera',    '555-0106', 'tenant', 7,  date(2023, 11, 5)),
            ('carlos@example.com',    'pass1234', 'Carlos',    'Reyes',      '555-0107', 'owner',  8,  date(2022, 7, 12)),
            ('elena@example.com',     'pass1234', 'Elena',     'Morales',    '555-0108', 'owner',  9,  date(2021, 4, 18)),
            ('roberto@example.com',   'pass1234', 'Roberto',   'Jiménez',    '555-0109', 'tenant', 10, date(2023, 9,  1)),
            ('patricia@example.com',  'pass1234', 'Patricia',  'Flores',     '555-0110', 'owner',  11, date(2020, 5, 30)),
            ('miguel@example.com',    'pass1234', 'Miguel',    'Ramírez',    '555-0111', 'tenant', 12, date(2024, 1, 15)),
            ('claudia@example.com',   'pass1234', 'Claudia',   'Ortiz',      '555-0112', 'owner',  14, date(2022, 10, 3)),
            ('jorge@example.com',     'pass1234', 'Jorge',     'Peña',       '555-0113', 'tenant', 15, date(2023, 3, 22)),
            ('fernanda@example.com',  'pass1234', 'Fernanda',  'Castro',     '555-0114', 'owner',  17, date(2021, 7,  8)),
            ('andres@example.com',    'pass1234', 'Andrés',    'Guzmán',     '555-0115', 'tenant', 18, date(2024, 4, 11)),
            ('valeria@example.com',   'pass1234', 'Valeria',   'Sánchez',    '555-0116', 'owner',  19, date(2022, 12, 1)),
            ('diego@example.com',     'pass1234', 'Diego',     'Mendoza',    '555-0117', 'tenant', 20, date(2023, 8, 17)),
            ('gabriela@example.com',  'pass1234', 'Gabriela',  'Ríos',       '555-0118', 'owner',  21, date(2021, 2, 28)),
            ('hector@example.com',    'pass1234', 'Héctor',    'Delgado',    '555-0119', 'tenant', 22, date(2024, 3,  5)),
            ('isabela@example.com',   'pass1234', 'Isabela',   'Romero',     '555-0120', 'owner',  23, date(2020, 11, 14)),
            ('mario@example.com',     'pass1234', 'Mario',     'Vega',       '555-0121', 'tenant', 24, date(2023, 5, 20)),
            ('natalia@example.com',   'pass1234', 'Natalia',   'Cruz',       '555-0122', 'owner',  25, date(2022, 9,  9)),
            ('oscar@example.com',     'pass1234', 'Óscar',     'Guerrero',   '555-0123', 'tenant', 26, date(2021, 6, 25)),
            ('paulina@example.com',   'pass1234', 'Paulina',   'Cabrera',    '555-0124', 'owner',  27, date(2024, 1, 30)),
            ('rafael@example.com',    'pass1234', 'Rafael',    'Navarro',    '555-0125', 'tenant', 29, date(2023, 7,  4)),
            ('silvia@example.com',    'pass1234', 'Silvia',    'Aguilar',    '555-0126', 'owner',  30, date(2022, 4, 16)),
            ('tomas@example.com',     'pass1234', 'Tomás',     'Medina',     '555-0127', 'tenant', 31, date(2021, 10, 7)),
        ]

        residents = []
        for email, password, first, last, phone, rtype, apt_idx, move_in in residents_data:
            user, u_created = User.objects.get_or_create(
                username=email,
                defaults=dict(email=email, first_name=first, last_name=last),
            )
            if u_created:
                user.set_password(password)
                user.save()

            resident, r_created = Resident.objects.get_or_create(
                user=user,
                defaults=dict(
                    phone=phone,
                    resident_type=rtype,
                    status='active',
                    move_in_date=move_in,
                    emergency_contact_name=f'Contacto de {first}',
                    emergency_contact_phone='555-9999',
                ),
            )
            if r_created:
                resident.apartments.add(apartments[apt_idx])
                self.stdout.write(f'  created resident {resident.full_name}')
            elif not resident.apartments.filter(pk=apartments[apt_idx].pk).exists():
                resident.apartments.add(apartments[apt_idx])
            residents.append(resident)

        return residents

    def _create_payments(self, apartments, residents):
        from apps.payments.models import Payment
        today = date.today()

        occupied_apts = [apt for apt in apartments if apt.status == 'occupied']
        apt_to_res = {}
        for res in residents:
            for apt in res.apartments.all():
                apt_to_res[apt.pk] = res

        for months_ago in range(6, 0, -1):
            period_date = today.replace(day=1) - timedelta(days=30 * months_ago)
            period = period_date.strftime('%Y-%m')
            due = period_date.replace(day=5)

            for i, apt in enumerate(occupied_apts):
                res = apt_to_res.get(apt.pk)
                if months_ago > 2:
                    status = 'paid'
                    paid_date = due + timedelta(days=i % 5)
                elif months_ago == 2:
                    status = 'overdue' if i % 4 == 0 else 'paid'
                    paid_date = due + timedelta(days=2) if status == 'paid' else None
                else:
                    if i % 4 == 0:
                        status = 'overdue'
                    elif i % 4 == 1:
                        status = 'submitted'
                    else:
                        status = 'pending'
                    paid_date = None

                _, created = Payment.objects.get_or_create(
                    apartment=apt,
                    period=period,
                    payment_type='maintenance',
                    defaults=dict(
                        resident=res,
                        amount=apt.monthly_fee,
                        status=status,
                        due_date=due,
                        paid_date=paid_date,
                        period=period,
                        reference=f'REF-{period}-{apt.number}' if status == 'paid' else '',
                    ),
                )
                if created:
                    self.stdout.write(f'  created payment {apt} {period}')

    def _create_announcements(self):
        from apps.announcements.models import Announcement
        admin = User.objects.filter(is_superuser=True).first()
        today = date.today()

        items = [
            ('Mantenimiento de elevadores', 'urgent',
             'Se realizará mantenimiento preventivo en todos los elevadores el próximo sábado de 8:00 a 14:00 hrs.', today + timedelta(days=5)),
            ('Asamblea ordinaria de condóminos', 'high',
             'Se convoca a todos los propietarios a la asamblea ordinaria del mes. Primer viernes a las 19:00 hrs.', today + timedelta(days=20)),
            ('Reglamento de uso de áreas comunes', 'normal',
             'Recordamos que el horario de uso de la piscina es de 7:00 a 22:00 hrs.', None),
            ('Bienvenida a nuevos residentes', 'low',
             'El equipo administrativo da la bienvenida a los nuevos residentes incorporados este mes.', None),
            ('Corte de agua programado', 'urgent',
             'El próximo miércoles de 9:00 a 13:00 hrs no habrá suministro de agua por mantenimiento de red.', today + timedelta(days=3)),
            ('Fumigación de áreas comunes', 'normal',
             'Se realizará fumigación preventiva en todas las áreas comunes el sábado de 7:00 a 10:00 hrs.', today + timedelta(days=8)),
            ('Nuevo reglamento de estacionamiento', 'high',
             'A partir del próximo mes se implementará el sistema de acceso con tarjeta para el estacionamiento.', today + timedelta(days=30)),
            ('Curso de primeros auxilios', 'low',
             'Invitamos a todos los residentes al curso gratuito de primeros auxilios el próximo sábado a las 10:00 hrs.', today + timedelta(days=12)),
        ]

        for title, priority, content, expiry in items:
            _, created = Announcement.objects.get_or_create(
                title=title,
                defaults=dict(content=content, priority=priority, author=admin,
                              is_active=True, expiry_date=expiry),
            )
            if created:
                self.stdout.write(f'  created announcement "{title}"')

    def _create_issues(self, apartments, residents):
        from apps.issues.models import Issue, IssueNote
        admin = User.objects.filter(is_superuser=True).first()
        staff = User.objects.filter(is_staff=True, is_superuser=False).first()
        now = timezone.now()

        items = [
            ('Fuga de agua en baño principal',        'plumbing',     'urgent', 'in_progress', apartments[0],  residents[0],  'Hay una fuga visible debajo del lavabo.',                         admin,  'Plomero asignado para el jueves.'),
            ('Luz fundida en pasillo piso 2',          'electrical',   'normal', 'open',        apartments[4],  residents[1],  'El foco del pasillo lleva tres días fundido.',                    None,   ''),
            ('Ruido excesivo departamento 202',        'noise',        'high',   'resolved',    apartments[5],  residents[2],  'Música a alto volumen después de las 23:00 hrs.',                 admin,  'Residente comprometido a respetar el reglamento.'),
            ('Puerta de estacionamiento no cierra',   'security',     'urgent', 'in_progress', None,           residents[3],  'La puerta automática del estacionamiento B1 falla desde el lunes.', admin, 'Técnico revisando el motor el viernes.'),
            ('Basura en área de jardín',               'common_areas', 'low',    'open',        None,           residents[4],  'Bolsas de basura abandonadas en zona de jardín.',                 None,   ''),
            ('Elevador lento torre Sirio',             'elevator',     'normal', 'open',        apartments[14], residents[5],  'El elevador tarda más de 5 minutos en responder.',                None,   ''),
            ('Goteras en techo departamento 401',      'plumbing',     'high',   'open',        apartments[11], residents[9],  'Cuando llueve hay goteras en la esquina del techo.',              None,   ''),
            ('Falla en intercomunicador',              'electrical',   'normal', 'in_progress', apartments[2],  residents[1],  'El intercomunicador de la entrada no funciona correctamente.',    staff,  'Revisión programada para el lunes.'),
            ('Humedad en paredes pasillo B',           'common_areas', 'normal', 'open',        None,           residents[6],  'Manchas de humedad en las paredes del pasillo B piso 3.',        None,   ''),
            ('Grifo cocina gotea constantemente',      'plumbing',     'low',    'resolved',    apartments[3],  residents[2],  'El grifo de la cocina gotea y desperdicia agua.',                 admin,  'Grifo reemplazado.'),
            ('Ventana rota departamento 103',          'other',        'normal', 'open',        apartments[2],  residents[1],  'El marco de la ventana está roto y no cierra bien.',             None,   ''),
            ('Falta iluminación en estacionamiento',  'electrical',   'high',   'in_progress', None,           residents[7],  'Zona de estacionamiento B2 sin luz desde hace una semana.',      staff,  'Se solicitó cotización para luminarias LED.'),
            ('Olor a gas en área de cocina común',    'security',     'urgent', 'resolved',    None,           residents[8],  'Se detectó olor a gas en la cocina del salón común.',            admin,  'Revisado por técnico certificado, fuga sellada.'),
            ('Daño en cancha de tenis',               'common_areas', 'low',    'open',        None,           residents[10], 'La red de la cancha está rota y el piso tiene grietas.',         None,   ''),
            ('Plaga de cucarachas en sótano',         'common_areas', 'high',   'in_progress', None,           residents[11], 'Se reportan cucarachas en el área de cuartos de servicio.',     admin,  'Fumigación programada para el sábado.'),
            ('Cortocircuito en lavandería',            'electrical',   'urgent', 'resolved',    None,           residents[12], 'Un cortocircuito apagó todas las lavadoras de la lavandería.',  admin,  'Tablero eléctrico reparado por electricista certificado.'),
            ('Filtración de agua en garaje',           'plumbing',     'high',   'open',        None,           residents[13], 'Agua filtrándose desde el piso superior al garaje.',            None,   ''),
            ('Alarma de incendio activándose sola',   'security',     'urgent', 'in_progress', None,           residents[14], 'La alarma se activa sin razón aparente en las noches.',         staff,  'Técnico de alarmas revisará el sistema el martes.'),
            ('Pérdida de señal en portón principal',  'security',     'normal', 'open',        None,           residents[15], 'El control remoto del portón principal pierde señal con frecuencia.', None, ''),
            ('Daño en azulejo baño comunal',          'common_areas', 'low',    'resolved',    None,           residents[16], 'Varios azulejos rotos en el baño comunal de la piscina.',       admin,  'Azulejos reemplazados.'),
            ('Calentador de agua sin funcionar',      'plumbing',     'high',   'open',        apartments[17], residents[5],  'El calentador lleva dos días sin calentar el agua.',            None,   ''),
            ('Ruido en tuberías al usar agua',        'plumbing',     'normal', 'open',        apartments[18], residents[6],  'Las tuberías hacen ruido golpeador al abrir el grifo.',         None,   ''),
            ('Mosquitero roto ventana sala',          'other',        'low',    'open',        apartments[19], residents[7],  'El mosquitero de la ventana de la sala está roto.',             None,   ''),
            ('Detector de humo sin batería',          'security',     'normal', 'resolved',    apartments[20], residents[8],  'El detector de humo emite pitido indicando batería baja.',      admin,  'Baterías reemplazadas en todos los detectores del piso.'),
            ('Elevador fuera de servicio Orión',      'elevator',     'urgent', 'in_progress', apartments[1],  residents[0],  'El elevador principal de Torre Orión está fuera de servicio.',  admin,  'Empresa de mantenimiento en camino.'),
        ]

        for idx, (title, category, priority, status, apt, reporter, desc, assigned, note_body) in enumerate(items):
            resolved_at = now if status == 'resolved' else None
            issue, created = Issue.objects.get_or_create(
                title=title,
                defaults=dict(
                    description=desc,
                    category=category,
                    priority=priority,
                    status=status,
                    apartment=apt,
                    reported_by=reporter,
                    assigned_to=assigned,
                    resolved_at=resolved_at,
                ),
            )
            if created:
                months_ago = (idx * 6) // len(items)
                backdated = now - timedelta(days=30 * months_ago + idx % 15)
                Issue.objects.filter(pk=issue.pk).update(created_at=backdated)
                IssueNote.objects.create(
                    issue=issue, status=status, body=note_body, created_by=assigned or admin,
                )
                self.stdout.write(f'  created issue "{title}"')
