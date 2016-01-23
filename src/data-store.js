import Sequelize from 'sequelize';

function defineMathItem(sequelize) {
    const MathItem = sequelize.define('mathitem', {
        id: {
            type: Sequelize.INTEGER,
            primaryKey: true,
            autoIncrement: true
        },
        item_type: {
            type: Sequelize.CHAR(1),
            allowNull: false
        },
        body: {
            type: Sequelize.TEXT,
            allowNull: false
        },
        created_at: {
            type: Sequelize.DATE,
            allowNull: false
        },
    }, {
        timestamps: false,
        underscored: true
    });
    MathItem.belongsTo(MathItem, {as: 'parent'});
    return MathItem;
}

function defineDraftItem(sequelize, MathItem) {
    const DraftItem = sequelize.define('draftitem', {
        id: {
            type: Sequelize.INTEGER,
            primaryKey: true,
            autoIncrement: true
        },
        item_type: {
            type: Sequelize.CHAR(1),
            allowNull: false
        },
        notes: {
            type: Sequelize.TEXT,
            allowNull: false
        },
        body: {
            type: Sequelize.TEXT,
            allowNull: false
        },
    }, {
        timestamps: true,
        underscored: true
    });
    DraftItem.belongsTo(MathItem, {as: 'parent'});
    return DraftItem;
}

export default class DataStore {
    constructor() {
        let sequelize = new Sequelize('teoremer', null, null, {
          dialect: 'sqlite',
          storage: './db.sqlite'
        });
        this.MathItem = defineMathItem(sequelize);
        this.DraftItem = defineDraftItem(sequelize, this.MathItem);
    }
    static get DEFINITION() {
        return 'D';
    }
    static get THEOREM() {
        return 'T';
    }
    static get PROOF() {
        return 'P';
    }
    init() {
        return Promise.all([
            this.MathItem.sync(),
            this.DraftItem.sync(),
        ]);
    }
    create_draft(item_type, body, notes) {
        return this.DraftItem.create({
            item_type,
            body,
            notes,
        }).then(item => item.id);
    }
    get_draft(id) {
        return this.DraftItem.findById(id);
    }
    get_draft_list() {
        return this.DraftItem.findAll({
            attributes: ['id', 'item_type', 'notes', 'updated_at']
        });
    }
}
